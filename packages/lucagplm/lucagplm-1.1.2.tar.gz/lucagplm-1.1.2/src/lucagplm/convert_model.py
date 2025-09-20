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
from lucagplm.modeling_lucagplm import LucaGPLMModel, LucaGPLMForPretraining
from lucagplm.configuration_lucagplm import LucaGPLMConfig
from lucagplm.tokenization_lucagplm import LucaGPLMTokenizer

def convert_old_weights(old_checkpoint_path, output_dir, with_pretraining_heads=False):
    # Path to the old checkpoint
    print(f"Loading old checkpoint from: {old_checkpoint_path}")
    print("=" * 80)
    
    # Load the model and tokenizer using the from_pretrained_old method
    try:
        if with_pretraining_heads:
            print("Converting model with pretraining heads...")
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
        
        # If we want pretraining heads, we need to load them from the old model
        if with_pretraining_heads:
            print("Loading pretraining heads from old model...")
            load_pretraining_heads(model, old_checkpoint_path)
        
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
        if with_pretraining_heads:
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
            if with_pretraining_heads:
                # For pretraining model, we don't need labels for a simple test
                outputs = test_model(test_input)
                print(f"✅ Forward pass successful! Output keys: {outputs.keys()}")
                if 'logits' in outputs:
                    print(f"Task logits: {list(outputs['logits'].keys())}")
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

def load_pretraining_heads(model, old_checkpoint_path):
    """
    Load pretraining heads from the old LucaVirus model
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
    
    # Create mapping for pretraining heads
    new_state_dict = OrderedDict()
    model_state_dict = model.state_dict()
    
    # Map LM head
    if "lm_head.weight" in old_state_dict and "lm_head.weight" in model_state_dict:
        new_state_dict["lm_head.weight"] = old_state_dict["lm_head.weight"]
    
    # Map pretraining task heads
    for task_level in ["token_level", "span_level", "seq_level"]:
        if task_level in model.pretrain_tasks:
            for task_name, task_head in model.pretrain_tasks[task_level].items():
                for component_name, component in task_head.items():
                    if component_name == "classifier_dropout":
                        continue  # Skip dropout layers as they don't have weights
                    
                    old_key = f"pretrain_tasks.{task_level}.{task_name}.{component_name}.weight"
                    old_bias_key = f"pretrain_tasks.{task_level}.{task_name}.{component_name}.bias"
                    
                    new_key = f"pretrain_tasks.{task_level}.{task_name}.{component_name}.weight"
                    new_bias_key = f"pretrain_tasks.{task_level}.{task_name}.{component_name}.bias"
                    
                    if old_key in old_state_dict and new_key in model_state_dict:
                        new_state_dict[new_key] = old_state_dict[old_key]
                    
                    if old_bias_key in old_state_dict and new_bias_key in model_state_dict:
                        new_state_dict[new_bias_key] = old_state_dict[old_bias_key]
    
    # Load the mapped state dict
    if new_state_dict:
        missing_keys, unexpected_keys = model.load_state_dict(new_state_dict, strict=False)
        
        if missing_keys:
            print(f"Warning: Missing keys when loading pretraining heads: {missing_keys}")
        if unexpected_keys:
            print(f"Warning: Unexpected keys when loading pretraining heads: {unexpected_keys}")
        
        print(f"Successfully loaded {len(new_state_dict)} pretraining head parameters from old model")
    else:
        print("No pretraining head parameters found in old model")

def convert_with_pretraining_heads(old_model_path, output_path):
    """
    转换带有预训练任务头的模型权重，直接在输出目录中保存带有预训练任务头的模型和tokenizer
    
    Args:
        old_model_path: 旧模型路径
        output_path: 输出路径
    """
    print("=" * 80)
    print("转换带有预训练任务头的模型权重")
    print("=" * 80)
    
    # 创建输出目录
    os.makedirs(output_path, exist_ok=True)
    
    # 加载旧模型权重
    print("\n🔄 加载旧模型权重...")
    old_weights_path_pth = os.path.join(old_model_path, "pytorch.pth")
    old_weights_path_pt = os.path.join(old_model_path, "pytorch.pt")
    
    old_state_dict = None
    if os.path.exists(old_weights_path_pth):
        old_state_dict = torch.load(old_weights_path_pth, map_location="cpu", weights_only=False)
    elif os.path.exists(old_weights_path_pt):
        old_state_dict = torch.load(old_weights_path_pt, map_location="cpu", weights_only=False)
    else:
        raise FileNotFoundError(f"旧模型权重未找到于 {old_weights_path_pth} 或 {old_weights_path_pt}")
    
    # 处理module.前缀
    print("🔄 处理module.前缀...")
    processed_old_state_dict = {}
    for key, value in old_state_dict.items():
        if key.startswith("module."):
            new_key = key[7:]  # 移除"module."前缀
            processed_old_state_dict[new_key] = value
        else:
            processed_old_state_dict[key] = value
    
    # 加载带有预训练任务头的模型
    print("🔄 加载带有预训练任务头的模型...")
    model = LucaGPLMForPretraining.from_pretrained_old(old_model_path)
    model.eval()
    
    # 获取模型状态字典
    new_state_dict = model.state_dict()
    
    # 识别与头相关的键
    print("\n🔍 识别与头相关的键...")
    
    # 旧模型中与头相关的键
    old_head_keys = [k for k in processed_old_state_dict.keys() if any(term in k for term in ["head", "lm_", "contact_head"])]
    print(f"旧模型中与头相关的键数量: {len(old_head_keys)}")
    for key in old_head_keys:
        print(f"  - {key} - 形状: {processed_old_state_dict[key].shape}")
    
    # 新模型中与头相关的键
    new_head_keys = [k for k in new_state_dict.keys() if any(term in k for term in ["head", "lm_", "classifier", "hidden_layer"])]
    print(f"\n新模型中与头相关的键数量: {len(new_head_keys)}")
    for key in new_head_keys:
        print(f"  - {key} - 形状: {new_state_dict[key].shape}")
    
    # 创建映射
    print("\n🔄 创建映射...")
    mapping = {}
    
    # 直接映射
    direct_mappings = {
        "lm_head.weight": "lm_head.weight"
    }
    
    for old_key, new_key in direct_mappings.items():
        if old_key in processed_old_state_dict and new_key in new_state_dict:
            mapping[old_key] = new_key
            print(f"✅ 直接映射: {old_key} -> {new_key}")
    
    # 应用映射
    print("\n🔄 应用映射...")
    converted_state_dict = {}
    
    # 首先复制所有新模型的原始权重
    for key, value in new_state_dict.items():
        converted_state_dict[key] = value.clone()
    
    # 然后应用映射
    for old_key, new_key in mapping.items():
        if old_key in processed_old_state_dict and new_key in new_state_dict:
            old_value = processed_old_state_dict[old_key]
            new_value_shape = new_state_dict[new_key].shape
            
            # 如果形状匹配，直接复制
            if old_value.shape == new_value_shape:
                converted_state_dict[new_key] = old_value.clone()
                print(f"✅ 映射: {old_key} -> {new_key}")
            else:
                print(f"⚠️  形状不匹配: {old_key} {old_value.shape} -> {new_key} {new_value_shape}")
                print(f"   将使用新模型的原始值")
    
    # 统计映射结果
    print("\n📊 统计信息:")
    print(f"  总映射数: {len(mapping)}")
    print(f"  成功映射数: {sum(1 for old_key, new_key in mapping.items() if old_key in processed_old_state_dict and new_key in new_state_dict)}")
    
    # 保存转换后的模型
    print("\n💾 保存转换后的模型...")
    model.load_state_dict(converted_state_dict)
    model.save_pretrained(output_path)
    
    # 加载并保存tokenizer
    print("\n🔄 加载并保存tokenizer...")
    tokenizer = LucaGPLMTokenizer.from_pretrained_old(old_model_path)
    tokenizer.save_pretrained(output_path)
    
    # 保存映射文件
    mapping_file = os.path.join(output_path, "final_mapping.json")
    with open(mapping_file, "w") as f:
        json.dump(mapping, f, indent=2)
    
    print(f"✅ 转换后的模型已保存到 {output_path}")
    print(f"✅ Tokenizer已保存到 {output_path}")
    print(f"✅ 映射文件已保存到 {mapping_file}")
    
    # 检查转换后的模型
    print("\n🔍 检查转换后的模型...")
    loaded_model = LucaGPLMForPretraining.from_pretrained(output_path)
    loaded_state_dict = loaded_model.state_dict()
    
    # 检查预训练任务头参数
    task_params = [k for k in loaded_state_dict.keys() if any(term in k for term in ["classifier", "hidden_layer", "lm_head"])]
    print(f"预训练任务头参数数: {len(task_params)}")
    
    # 检查pretrain_tasks字典结构
    print("\n🔍 检查pretrain_tasks字典结构:")
    if hasattr(loaded_model, 'pretrain_tasks'):
        print("  ✅ 模型包含pretrain_tasks字典")
        
        # 检查token_level任务
        if "token_level" in loaded_model.pretrain_tasks:
            print("  ✅ 包含token_level任务")
            for task_name in loaded_model.pretrain_tasks["token_level"]:
                print(f"    - {task_name}")
        else:
            print("  ❌ 不包含token_level任务")
        
        # 检查span_level任务
        if "span_level" in loaded_model.pretrain_tasks:
            print("  ✅ 包含span_level任务")
            for task_name in loaded_model.pretrain_tasks["span_level"]:
                print(f"    - {task_name}")
        else:
            print("  ❌ 不包含span_level任务")
        
        # 检查seq_level任务
        if "seq_level" in loaded_model.pretrain_tasks:
            print("  ✅ 包含seq_level任务")
            for task_name in loaded_model.pretrain_tasks["seq_level"]:
                print(f"    - {task_name}")
        else:
            print("  ❌ 不包含seq_level任务")
    else:
        print("  ❌ 模型不包含pretrain_tasks字典")
    
    # 测试tokenizer
    print("\n🔍 测试tokenizer...")
    test_tokenizer = LucaGPLMTokenizer.from_pretrained(output_path)
    test_sequence = "ATCGATCGATCG"  # Example gene sequence
    encoded = test_tokenizer.encode(test_sequence, add_special_tokens=True)
    decoded = test_tokenizer.decode(encoded)
    print(f"✅ Tokenizer测试成功! 输入: {test_sequence}, 编码: {encoded}, 解码: {decoded}")
    
    return mapping

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
        "--with-pretraining-heads",
        action="store_true",
        help="Whether to include pretraining heads in the converted model"
    )
    
    parser.add_argument(
        "--convert-with-pretraining-heads",
        action="store_true",
        help="Convert model weights with pretraining heads directly from old model"
    )
    
    return parser.parse_args()

def main():
    """Main entry point for the command line interface."""
    args = parse_arguments()
    
    if args.convert_with_pretraining_heads:
        # 使用新的转换模式
        if not args.old_checkpoint:
            print("错误: --convert-with-pretraining-heads 模式需要 --old-checkpoint 参数")
            sys.exit(1)
            
        print("转换带有预训练任务头的模型权重...")
        print(f"旧模型路径: {args.old_checkpoint}")
        print(f"输出目录: {args.output_dir}")
        print()
        
        try:
            mapping = convert_with_pretraining_heads(args.old_checkpoint, args.output_dir)
            print(f"\n🎉 转换完成！")
            print(f"转换后的模型已保存到 '{args.output_dir}'")
        except Exception as e:
            print(f"\n💥 转换失败: {e}")
            import traceback
            traceback.print_exc()
    else:
        # 使用原有的转换模式
        if not args.old_checkpoint:
            print("错误: 需要 --old-checkpoint 参数")
            sys.exit(1)
            
        print("转换LucaOneVirus检查点到LucaGPLMModel格式...")
        print(f"旧检查点: {args.old_checkpoint}")
        print(f"输出目录: {args.output_dir}")
        print(f"包含预训练头: {args.with_pretraining_heads}")
        print()
        
        success = convert_old_weights(args.old_checkpoint, args.output_dir, args.with_pretraining_heads)
        
        if success:
            print(f"\n🎉 转换完成！")
            print(f"转换后的模型已保存为 '{args.output_dir}'")
        else:
            print("\n💥 转换失败。请检查上面的错误信息。")

if __name__ == "__main__":
    main()