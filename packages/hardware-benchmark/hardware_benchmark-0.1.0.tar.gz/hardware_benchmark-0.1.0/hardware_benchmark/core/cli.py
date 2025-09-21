#!/usr/bin/env python3
"""
Command line interface module - handles command line arguments and parameter validation
"""

import argparse
import sys
import torch
import logging
from core.config import DETECTION_MODELS, CLASSIFICATION_MODELS, SEGMENTATION_MODELS, SAMPLE_OPTIONS
from models.models import validate_model_availability

class CommandLineInterface:
    """Command line interface class"""
    
    def __init__(self, dependencies):
        self.dependencies = dependencies
        self.logger = logging.getLogger(__name__)
    
    def create_parser(self):
        """Create command line argument parser"""
        parser = argparse.ArgumentParser(
            description='Deep Learning Model Benchmark Tool',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Example usage:
  # Test ResNet18 classification model using CPU
  python main.py --device cpu --model-type classification --model resnet18 --dataset MNIST --samples 100
  
  # Test YOLOv8 detection model using GPU  
  python main.py --device cuda:0 --model-type detection --model yolov8n --dataset Test-Images --samples 500
  
  # Test segmentation model with auto device selection
  python main.py --device auto --model-type segmentation --model unet_resnet34 --dataset Synthetic-Segmentation --samples 200
  
  # List available models
  python main.py --list-models
  
  # List available datasets  
  python main.py --list-datasets
            """
        )
        
        # Add various command line arguments
        parser.add_argument('--device', 
                          choices=['cpu', 'cuda:0', 'auto'], 
                          default='auto',
                          help='Computing device selection:\n'
                               '  cpu - Force CPU computation\n'
                               '  cuda:0 - Force GPU computation\n'
                               '  auto - Auto selection (use GPU if available, otherwise CPU)\n'
                               '  (default: auto)')
        
        parser.add_argument('--model-type', 
                          choices=['classification', 'detection', 'segmentation'],
                          help='Model type (required)\n'
                               '  classification - Image classification tasks\n'
                               '  detection - Object detection tasks\n'
                               '  segmentation - Semantic segmentation tasks')
        
        parser.add_argument('--model',
                          help='Model name (required, use --list-models to see available models)')
        
        parser.add_argument('--dataset',
                          help='Dataset name (required, use --list-datasets to see available datasets)')
        
        parser.add_argument('--samples', 
                          type=int, 
                          default=100,
                          help='Number of test samples (default: 100, -1 means all)')
        
        parser.add_argument('--batch-size',
                          type=int,
                          default=1,
                          help='Batch size (default: 1)')
        
        parser.add_argument('--output-dir',
                          default='./results',
                          help='Output directory (default: ./results)')
        
        parser.add_argument('--no-plots',
                          action='store_true',
                          help='Do not generate visualization plots')
        
        parser.add_argument('--quiet',
                          action='store_true',
                          help='Quiet mode, reduce output')
        
        parser.add_argument('--list-models',
                          action='store_true',
                          help='List all available models')
        
        parser.add_argument('--list-datasets',
                          action='store_true',
                          help='List all available datasets')
        
        # Monitoring related parameters
        parser.add_argument('--disable-gpu-monitor',
                          action='store_true',
                          help='Disable detailed GPU monitoring')
        
        parser.add_argument('--monitor-interval',
                          type=float,
                          default=0.1,
                          help='Monitoring sampling interval (seconds) (default: 0.1)')
        
        parser.add_argument('--monitor-samples',
                          type=int,
                          default=1000,
                          help='Maximum monitoring samples (default: 1000)')
        
        return parser
    
    def list_available_models(self):
        """List all available models"""
        print("Available Models List:")
        print("="*60)
        
        # Classification models
        print("\nImage Classification Models (Classification):")
        print("Usage: --model-type classification --model <model_name>")
        if validate_model_availability('classification', self.dependencies):
            for key, model in CLASSIFICATION_MODELS.items():
                status = "✓" if self.dependencies['timm'] else "✗"
                print(f"  {status} {model['model']:<25} - {model['name']}")
        else:
            print("  Required installation: pip install timm")
        
        # Detection models
        print("\nObject Detection Models (Detection):")
        print("Usage: --model-type detection --model <model_name>")
        if validate_model_availability('detection', self.dependencies):
            for key, model in DETECTION_MODELS.items():
                if model['type'] == 'yolo':
                    status = "✓" if self.dependencies['ultralytics'] else "✗"
                    req = "ultralytics" if not self.dependencies['ultralytics'] else ""
                    # Show both formats: with .pt and without .pt
                    model_name = model['model']
                    if model_name.endswith('.pt'):
                        model_id = f"{model_name} or {model_name[:-3]}"
                    else:
                        model_id = model_name
                elif model['type'] == 'torchvision':
                    status = "✓" if self.dependencies['torchvision_detection'] else "✗"
                    req = "torchvision (latest version)" if not self.dependencies['torchvision_detection'] else ""
                    model_id = model['model'].replace('_', '-')
                else:
                    status = "✗"
                    req = "unknown dependency"
                    model_id = model['model']
                
                print(f"  {status} {model_id:<30} - {model['name']}")
                if req:
                    print(f"    Required installation: pip install {req}")
        else:
            print("  Required installation: pip install ultralytics or update torchvision")
        
        # Segmentation models
        print("\nSemantic Segmentation Models (Segmentation):")
        print("Usage: --model-type segmentation --model <model_name>")
        if validate_model_availability('segmentation', self.dependencies):
            for key, model in SEGMENTATION_MODELS.items():
                status = "✓" if self.dependencies['smp'] else "✗"
                model_id = f"{model['model'].lower()}_{model['encoder'].replace('-', '_')}"
                print(f"  {status} {model_id:<25} - {model['name']}")
        else:
            print("  Required installation: pip install segmentation-models-pytorch")
        
        # Computing device selection description
        print("\nComputing Device Selection (--device):")
        print("="*40)
        cuda_available = torch.cuda.is_available()
        if cuda_available:
            device_name = torch.cuda.get_device_name(0)
            print(f"  ✓ cpu      - Use CPU computation (always available)")
            print(f"  ✓ cuda:0   - Use GPU computation: {device_name}")
            print(f"  ✓ auto     - Auto selection (recommended, will choose: GPU)")
        else:
            print(f"  ✓ cpu      - Use CPU computation (always available)")
            print(f"  ✗ cuda:0   - Use GPU computation (CUDA unavailable)")
            print(f"  ✓ auto     - Auto selection (recommended, will choose: CPU)")
    
    def list_available_datasets(self):
        """List all available datasets"""
        print("Available Datasets List:")
        print("="*60)
        
        print("\nClassification Datasets (--model-type classification):")
        print("  MNIST              - Handwritten digit recognition (28x28 -> 224x224)")
        print("  CIFAR-10           - Small object classification (32x32 -> 224x224)")
        print("  ImageNet-Sample    - Synthetic ImageNet samples (224x224)")
        
        print("\nDetection Datasets (--model-type detection):")
        print("  COCO-Sample        - Synthetic COCO samples")
        print("  KITTI              - Autonomous driving scene data")
        print("  Test-Images        - Preset test images")
        
        print("\nSegmentation Datasets (--model-type segmentation):")
        print("  Cityscapes         - Urban street scene segmentation")
        print("  Synthetic-Segmentation - Synthetic segmentation data")
        
        print("\nUsage Examples:")
        print("  python main.py --model-type classification --model resnet18 --dataset MNIST --device auto")
        print("  python main.py --model-type detection --model yolov8n --dataset Test-Images --device cuda:0")
        print("  python main.py --model-type segmentation --model unet_resnet34 --dataset Cityscapes --device cpu")
    
    def validate_args(self, args):
        """Validate command line arguments"""
        errors = []
        
        # Validate device
        if args.device == 'cuda:0' and not torch.cuda.is_available():
            errors.append("Specified CUDA device but CUDA is not available. Please use --device cpu or --device auto")
        
        # Validate model type availability
        if args.model_type:
            if not validate_model_availability(args.model_type, self.dependencies):
                if args.model_type == 'classification':
                    errors.append("Classification models unavailable, required installation: pip install timm")
                elif args.model_type == 'detection':
                    errors.append("Detection models unavailable, required installation: pip install ultralytics")
                elif args.model_type == 'segmentation':
                    errors.append("Segmentation models unavailable, required installation: pip install segmentation-models-pytorch")
        
        # Validate model name
        if args.model_type and args.model:
            valid_model = self._validate_model_name(args.model_type, args.model)
            if not valid_model:
                errors.append(f"Invalid model name: {args.model}")
                errors.append(f"Please use --list-models to see available models for {args.model_type} type")
        
        # Validate dataset name
        if args.model_type and args.dataset:
            valid_dataset = self._validate_dataset_name(args.model_type, args.dataset)
            if not valid_dataset:
                errors.append(f"Invalid dataset name: {args.dataset}")
                errors.append(f"Please use --list-datasets to see available datasets for {args.model_type} type")
        
        # Validate sample count
        if args.samples < -1 or args.samples == 0:
            errors.append("Sample count must be positive or -1 (meaning all)")
        
        return errors
    
    def _validate_model_name(self, model_type, model_name):
        """Validate if model name is valid"""
        if model_type == 'classification':
            valid_models = [model['model'] for model in CLASSIFICATION_MODELS.values()]
            return model_name in valid_models
        
        elif model_type == 'detection':
            valid_models = []
            for model in DETECTION_MODELS.values():
                if model['type'] == 'yolo':
                    # YOLO models support both .pt and non-.pt formats
                    valid_models.append(model['model'])
                    if model['model'].endswith('.pt'):
                        valid_models.append(model['model'][:-3])  # Remove .pt suffix
                else:
                    # torchvision models use underscore format
                    valid_models.append(model['model'])
                    valid_models.append(model['model'].replace('_', '-'))
            return model_name in valid_models
        
        elif model_type == 'segmentation':
            valid_models = []
            for model in SEGMENTATION_MODELS.values():
                model_id = f"{model['model'].lower()}_{model['encoder'].replace('-', '_')}"
                valid_models.append(model_id)
            return model_name in valid_models
        
        return False
    
    def _validate_dataset_name(self, model_type, dataset_name):
        """Validate if dataset name is valid"""
        valid_datasets = {
            'classification': ['MNIST', 'CIFAR-10', 'ImageNet-Sample'],
            'detection': ['COCO-Sample', 'KITTI', 'Test-Images'],
            'segmentation': ['Cityscapes', 'Synthetic-Segmentation']
        }
        
        return dataset_name in valid_datasets.get(model_type, [])
    
    def args_to_config(self, args):
        """Convert command line arguments to configuration object"""
        # Auto-select device and record selection logic
        if args.device == 'auto':
            if torch.cuda.is_available():
                device = 'cuda:0'
                device_choice_reason = "Auto-selected GPU (CUDA available)"
            else:
                device = 'cpu'
                device_choice_reason = "Auto-selected CPU (CUDA unavailable)"
        else:
            device = args.device
            if device == 'cpu':
                device_choice_reason = "User specified CPU"
            elif device == 'cuda:0':
                device_choice_reason = "User specified GPU"
            else:
                device_choice_reason = f"User specified device: {device}"
        
        # Log device selection information
        self.logger.info(f"Device selection: {device} ({device_choice_reason})")
        
        # Find model information
        model_info = self._find_model_info(args.model_type, args.model)
        
        config = {
            'device': device,
            'device_choice_reason': device_choice_reason,
            'model_type': args.model_type,
            'model_info': model_info,
            'dataset_name': args.dataset,
            'test_samples': args.samples,
            'batch_size': args.batch_size,
            'output_dir': args.output_dir,
            'no_plots': args.no_plots,
            'quiet': args.quiet
        }
        
        return config
    
    def _find_model_info(self, model_type, model_name):
        """Find model information based on model name"""
        if model_type == 'classification':
            for model in CLASSIFICATION_MODELS.values():
                if model['model'] == model_name:
                    return model
        
        elif model_type == 'detection':
            for model in DETECTION_MODELS.values():
                if model['type'] == 'yolo':
                    # Support both yolov8n and yolov8n.pt formats
                    if model['model'] == model_name or model['model'] == f"{model_name}.pt":
                        return model
                    if model['model'].endswith('.pt') and model['model'][:-3] == model_name:
                        return model
                elif model['type'] == 'torchvision':
                    if model['model'] == model_name or model['model'].replace('_', '-') == model_name:
                        return model
        
        elif model_type == 'segmentation':
            for model in SEGMENTATION_MODELS.values():
                model_id = f"{model['model'].lower()}_{model['encoder'].replace('-', '_')}"
                if model_id == model_name:
                    return model
        
        return None
    
    def print_config_summary(self, config):
        """Print configuration summary"""
        if not config.get('quiet', False):
            print("\n" + "="*60)
            print("Benchmark Test Configuration:")
            print("="*60)
            print(f"Computing Device: {config['device']} ({config.get('device_choice_reason', 'Unknown reason')})")
            if config['device'].startswith('cuda') and torch.cuda.is_available():
                device_name = torch.cuda.get_device_name(0)
                memory_gb = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                print(f"GPU Info: {device_name} ({memory_gb:.1f}GB)")
            print(f"Model Type: {config['model_type']}")
            print(f"Model: {config['model_info']['name']}")
            print(f"Dataset: {config['dataset_name']}")
            print(f"Samples: {config['test_samples'] if config['test_samples'] != -1 else 'All'}")
            print(f"Output Directory: {config['output_dir']}")
            print(f"Generate Plots: {'No' if config['no_plots'] else 'Yes'}")
            print(f"Quiet Mode: {'Yes' if config['quiet'] else 'No'}")
            print("="*60)