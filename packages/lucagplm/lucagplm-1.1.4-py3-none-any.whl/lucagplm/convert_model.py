#!/usr/bin/env python3
"""
Script to convert old LucaOneVirus checkpoint to new LucaGPLMModel format
"""

import os
import sys
import torch
import argparse
import json
from collections import OrderedDict
from .modeling_lucagplm import LucaGPLMModel, LucaGPLMForPretraining
from .configuration_lucagplm import LucaGPLMConfig
from .tokenization_lucagplm import LucaGPLMTokenizer

def convert_old_weights(old_checkpoint_path, output_dir, with_lm_head=False):
    # Path to the old checkpoint
    print(f"Loading old checkpoint from: {old_checkpoint_path}")
    print("=" * 80)
    
    # Load the model and tokenizer using the from_pretrained_old method
    try:
        if with_lm_head:
            print("Converting model with lm head...")
            model = LucaGPLMForPretraining.from_pretrained_old(
                old_model_path=old_checkpoint_path,
                config=None,  # Let it auto-convert the config
            )
        else:
            model = LucaGPLMModel.from_pretrained_old(
                old_model_path=old_checkpoint_path,
                config=None,  # Let it auto-convert the config
                add_pooling_layer=True
            )
        
        # Load the tokenizer using from_pretrained_old method
        tokenizer = LucaGPLMTokenizer.from_pretrained_old(old_checkpoint_path)
        
        print("✅ Successfully loaded and converted the old model and tokenizer!")
        print(f"Model config: {model.config}")
        print(f"Number of parameters: {sum(p.numel() for p in model.parameters()):,}")
        print(f"Tokenizer vocab size: {tokenizer.vocab_size}")
        print(f"Tokenizer vocab type: {tokenizer.vocab_type}")
        
        # If we want lm head, we need to load it from the old model
        if with_lm_head:
            print("Loading lm head from old model...")
            load_lm_head(model, old_checkpoint_path)
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Save the model and tokenizer in the new format
        print(f"\nSaving converted model and tokenizer to: {output_dir}")
        model.save_pretrained(output_dir)
        tokenizer.save_pretrained(output_dir)
        
        print(f"✅ Model and tokenizer successfully saved as: {output_dir}")
        print("=" * 80)
        
        # Test loading the converted model and tokenizer
        print("Testing the converted model and tokenizer...")
        if with_lm_head:
            test_model = LucaGPLMForPretraining.from_pretrained(output_dir)
        else:
            test_model = LucaGPLMModel.from_pretrained(output_dir)
        test_tokenizer = LucaGPLMTokenizer.from_pretrained(output_dir)
        print(f"✅ Successfully loaded converted model and tokenizer from {output_dir}")
        print(f"Test model config: {test_model.config}")
        print(f"Test tokenizer vocab size: {test_tokenizer.vocab_size}")
        
        # Simple forward pass test
        print("\nRunning a simple forward pass test...")
        test_input = torch.randint(0, 39, (1, 100))  # vocab_size = 39
        with torch.no_grad():
            if with_lm_head:
                # For pretraining model, we don't need labels for a simple test
                outputs = test_model(test_input)
                print(f"✅ Forward pass successful! Output keys: {outputs.keys()}")
                if 'logits' in outputs:
                    print(f"Task logits shape: {outputs['logits'].shape}")
            else:
                outputs = test_model(test_input)
                print(f"✅ Forward pass successful! Output shape: {outputs.last_hidden_state.shape}")
        
        # Test tokenizer functionality
        print("\nTesting tokenizer functionality...")
        test_sequence = "ATCGATCGATCG"  # Example gene sequence
        encoded = test_tokenizer.encode(test_sequence, add_special_tokens=True)
        decoded = test_tokenizer.decode(encoded)
        print(f"✅ Tokenizer test successful! Input: {test_sequence}, Encoded: {encoded}, Decoded: {decoded}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

def load_lm_head(model, old_checkpoint_path):
    """
    Load lm head from the old LucaVirus model
    """
    # Load old model weights
    old_weights_path_pth = os.path.join(old_checkpoint_path, "pytorch.pth")
    old_weights_path_pt = os.path.join(old_checkpoint_path, "pytorch.pt")
    
    old_state_dict = None
    if os.path.exists(old_weights_path_pth):
        old_state_dict = torch.load(old_weights_path_pth, map_location="cpu", weights_only=False)
    elif os.path.exists(old_weights_path_pt):
        old_state_dict = torch.load(old_weights_path_pt, map_location="cpu", weights_only=False)
    else:
        print(f"Warning: Could not find old model weights at {old_weights_path_pth} or {old_weights_path_pt}")
        return
    
    # Handle wrapped models (remove 'module.' prefix if present)
    if isinstance(old_state_dict, dict):
        new_old_state_dict = OrderedDict()
        for k, v in old_state_dict.items():
            name = k[7:] if k.startswith("module.") else k
            new_old_state_dict[name] = v
        old_state_dict = new_old_state_dict
    else:
        # If it's a model object, get state dict
        old_state_dict = old_state_dict.state_dict()
    
    # Create mapping for lm head
    new_state_dict = OrderedDict()
    model_state_dict = model.state_dict()
    
    # Map LM head
    if "lm_head.weight" in old_state_dict and "lm_head.weight" in model_state_dict:
        new_state_dict["lm_head.weight"] = old_state_dict["lm_head.weight"]
        print(f"✅ 映射lm head权重: lm_head.weight")
    
    # Load the mapped state dict
    if new_state_dict:
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
        
        if missing_keys:
            print(f"Warning: Missing keys when loading lm head: {missing_keys}")
        if unexpected_keys:
            print(f"Warning: Unexpected keys when loading lm head: {unexpected_keys}")
        
        print(f"Successfully loaded {len(new_state_dict)} lm head parameters from old model")
    else:
        print("No lm head parameters found in old model")

def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Convert old LucaOneVirus checkpoint to new LucaGPLMModel format",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )
    
    parser.add_argument(
        "--old-checkpoint",
        type=str,
        help="Path to the old checkpoint directory to convert"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        required=True,
        help="Output directory name/path for the converted model"
    )
    
    parser.add_argument(
        "--with-lm-head",
        action="store_true",
        help="Whether to include lm head in the converted model"
    )
    
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    if not args.old_checkpoint:
        print("错误: 需要 --old-checkpoint 参数")
        sys.exit(1)
        
    print("转换LucaOneVirus检查点到LucaGPLMModel格式...")
    print(f"旧检查点: {args.old_checkpoint}")
    print(f"输出目录: {args.output_dir}")
    print(f"包含lm head: {args.with_lm_head}")
    print()
    
    success = convert_old_weights(args.old_checkpoint, args.output_dir, args.with_lm_head)
    
    if success:
        print(f"\n🎉 转换完成！")
        print(f"转换后的模型已保存为 '{args.output_dir}'")
    else:
        print("\n💥 转换失败。请检查上面的错误信息。")