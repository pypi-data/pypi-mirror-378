#!/usr/bin/env python3
"""
OpenSloth - Simple Multi-GPU Training with torchrun

This is the new simplified approach for multi-GPU training using PyTorch's built-in
Distributed Data Parallel (DDP) via torchrun.

Usage:
    # Single GPU
    python train_scripts/train_ddp.py
    
    # Multi-GPU (recommended)
    torchrun --nproc_per_node=2 train_scripts/train_ddp.py
    torchrun --nproc_per_node=4 train_scripts/train_ddp.py
    
Key benefits:
- No complex configuration files needed
- Uses standard PyTorch DDP (torchrun)
- Works with any Unsloth model
- Simple and clean codebase
- Automatic GPU detection and setup
- Efficient sequence packing with 4D masked attention for better GPU utilization

Requirements:
- unsloth
- transformers (latest version supporting 4D masks)
- trl
- datasets
- flash-attn (pip install flash-attn --no-build-isolation)
"""

import os
import random
import pandas as pd
from unsloth import FastLanguageModel
from datasets import Dataset
from trl import SFTConfig, SFTTrainer

# Import our simple DDP patch for Unsloth compatibility
from opensloth.patching.ddp_patch import ddp_patch
ddp_patch()

# -----------------------------
# Model Configuration
# -----------------------------
max_seq_length = 8000  # Increased sequence length for better packing efficiency (model supports up to 32768)
lora_rank = 8          # LoRA rank for efficient training

# Get local rank for DDP - torchrun sets this automatically
local_rank = int(os.environ.get("LOCAL_RANK", 0))

print(f"🚀 Initializing training on GPU {local_rank}")

# IMPORTANT: For 4-bit models under DDP, you MUST load on the correct GPU per rank
# This ensures each process loads the model on its assigned GPU
model, tokenizer = FastLanguageModel.from_pretrained(
    model_name="unsloth/Qwen3-0.6B",  # Using small model for quick testing
    max_seq_length=max_seq_length,
    load_in_4bit=True,                # Memory efficient 4-bit loading
    # attn_implementation="flash_attention_2",  # Required for 4D masked packing to prevent cross-contamination
    device_map={"": local_rank},      # Each process gets its own GPU
)

# Apply LoRA adapter for efficient fine-tuning
# WARNING: Do NOT call .to(device) afterwards for 4-bit models - this will break DDP!
model = FastLanguageModel.get_peft_model(
    model,
    r=lora_rank,                                    # LoRA rank
    target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],  # Target attention layers
    lora_alpha=lora_rank * 2,                      # LoRA alpha (typically 2x rank)
    use_gradient_checkpointing="unsloth",           # Memory efficient training
    random_state=42,                               # Reproducible results
)

# -----------------------------
# Dataset Generation
# -----------------------------

def get_random_realistic_fake_data(n: int = 100, seed: int = 3407):
    """
    Generate a realistic but fake dataset for training demonstration.
    
    This creates a mix of math problems and trivia questions with their solutions,
    formatted as conversational data that works well with chat models.
    
    Args:
        n (int): Number of examples to generate
        seed (int): Random seed for reproducibility
    
    Returns:
        Dataset: Hugging Face dataset ready for training
    """
    random.seed(seed)
    print(f"📊 Generating {n} training examples...")

    # Question templates for variety
    math_templates = [
        ("What is {a} + {b}?", lambda a, b: f"The answer is {a+b}."),
        ("What is {a} - {b}?", lambda a, b: f"The answer is {a-b}."),
        ("Multiply {a} and {b}.", lambda a, b: f"The result is {a*b}."),
    ]

    trivia_templates = [
        ("What is the capital of {country}?", lambda country, capital: f"The capital of {country} is {capital}."),
        ("Who wrote {work}?", lambda work, author: f"{work} was written by {author}."),
        ("In which year did {event} happen?", lambda event, year: f"{event} happened in {year}."),
    ]

    # Knowledge base for trivia questions
    countries = {"France": "Paris", "Japan": "Tokyo", "Germany": "Berlin", "Italy": "Rome"}
    works = {"Hamlet": "William Shakespeare", "1984": "George Orwell", "The Odyssey": "Homer"}
    events = {"WW2 end": 1945, "Moon landing": 1969, "Fall of Berlin Wall": 1989}

    problems, solutions = [], []
    
    for _ in range(n):
        if random.random() < 0.5:  # 50% math problems
            tmpl, answer_fn = random.choice(math_templates)
            a, b = random.randint(1, 20), random.randint(1, 20)
            problems.append(tmpl.format(a=a, b=b))
            solutions.append(answer_fn(a, b))
        else:  # 50% trivia questions
            tmpl, answer_fn = random.choice(trivia_templates)
            if "capital" in tmpl:
                country, capital = random.choice(list(countries.items()))
                problems.append(tmpl.format(country=country))
                solutions.append(answer_fn(country, capital))
            elif "wrote" in tmpl:
                work, author = random.choice(list(works.items()))
                problems.append(tmpl.format(work=work))
                solutions.append(answer_fn(work, author))
            else:  # historical events
                event, year = random.choice(list(events.items()))
                problems.append(tmpl.format(event=event))
                solutions.append(answer_fn(event, year))

    # Create structured dataset
    fake_data = {"problem": problems, "generated_solution": solutions}
    df = pd.DataFrame(fake_data)
    
    # Format as chat conversations
    df["Messages"] = df.apply(
        lambda x: [
            {"role": "user", "content": x["problem"]},
            {"role": "assistant", "content": x["generated_solution"]},
        ],
        axis=1,
    )
    
    # Apply chat template for the model
    df["text"] = tokenizer.apply_chat_template(df["Messages"].tolist(), tokenize=False)
    dataset = Dataset.from_pandas(df)
    return dataset



# Create training and validation datasets
train_dataset = get_random_realistic_fake_data(n=10000, seed=42)
val_dataset = get_random_realistic_fake_data(n=20, seed=2024)

# -----------------------------
# Training Configuration
# -----------------------------

# Auto-detect world size (number of GPUs) - torchrun sets this automatically
world_size = int(os.environ.get("WORLD_SIZE", "1"))
print(f"🌍 World size: {world_size} GPU(s)")

# Smart gradient accumulation: fewer steps for multi-GPU to maintain same effective batch size
grad_accum = 1 if world_size > 1 else 2
effective_batch_size = 1 * grad_accum * world_size

print("📊 Batch configuration:")
print("   - Per device batch size: 1")
print(f"   - Gradient accumulation: {grad_accum}")
print(f"   - Effective batch size: {effective_batch_size}")

trainer = SFTTrainer(
    model=model,
    tokenizer=tokenizer, # type: ignore
    train_dataset=train_dataset,
    eval_dataset=val_dataset,
    
    args=SFTConfig(
        per_device_train_batch_size=1,      # Small batch per GPU for memory efficiency
        gradient_accumulation_steps=grad_accum,  # Accumulate gradients for larger effective batch
        num_train_epochs=10,                # Number of epochs to train
        learning_rate=2e-4,                 # Learning rate for training
        logging_steps=1,                    # Log every step for monitoring
        save_strategy="no",                 # Don't save checkpoints for this demo
        output_dir=f"outputs/debug_worldsize{world_size}",  # Output directory
        ddp_find_unused_parameters=False,   # DDP optimization
        report_to="tensorboard",            # Use tensorboard for logging
        eval_strategy="epoch",              # Evaluate at end of each epoch
        # packing=True,
        
        # Packing configuration for 4D masked sequence packing
        # packing=True,                       # Enable sequence packing with 4D masks
        # packing_strategy="bfd",             # Best-fit decreasing strategy for efficient packing
        # max_length=max_seq_length,          # Max length for packed sequences (matches model config)
        # padding_free=True,                  # Padding-free processing (enabled with packing)
        dataset_num_proc=4,
    ),  
)

# -----------------------------
# Start Training
# -----------------------------
print("🔥 Starting training with 4D masked sequence packing...")
if local_rank == 0:  # Only print from main process
    print(f"💾 Logs will be saved to: outputs/debug_worldsize{world_size}")
    print(f"📈 Monitor training: tensorboard --logdir outputs/debug_worldsize{world_size}")

trainer.train()

if local_rank == 0:  # Only print from main process
    print("✅ Training completed successfully!")
    print(f"🎯 Model trained for {trainer.state.epoch} epochs")
    print(f"📊 Total steps: {trainer.state.global_step}")