import random
from typing import Optional
import numpy as np
import torch
from diffusers.utils.torch_utils import is_compiled_module
from accelerate import Accelerator


def tokenize_captions(examples, tokenizer, caption_column, is_train=True):
    '''
    Adapted from The HuggingFace Inc. team. All rights reserved.
    Licensed under the Apache License, Version 2.0.
    Source: https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py
    '''
    captions = []
    for caption in examples[caption_column]:
        if isinstance(caption, str):
            captions.append(caption)
        elif isinstance(caption, (list, np.ndarray)):
            # take a random caption if there are multiple
            captions.append(random.choice(caption) if is_train else caption[0])
        else:
            raise ValueError(
                f"Caption column `{caption_column}` should contain either strings or lists of strings."
            )
    inputs = tokenizer(
        captions, max_length=tokenizer.model_max_length, padding="max_length", truncation=True, return_tensors="pt"
    )
    return inputs.input_ids


def unwrap_model(model, accelerator):
    '''
    Adapted from The HuggingFace Inc. team. All rights reserved.
    Licensed under the Apache License, Version 2.0.
    Source: https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py
    '''
    model = accelerator.unwrap_model(model)
    model = model._orig_mod if is_compiled_module(model) else model
    return model


def forget_tokens(examples, tokenizer, caption_column, forget_prompt: str):
    length = len(examples[caption_column])
    captions = [forget_prompt] * length
    inputs = tokenizer(
        captions, max_length=tokenizer.model_max_length, padding="max_length", truncation=True, return_tensors="pt"
    )
    return inputs.input_ids
    
def preprocess_train(examples, tokenizer, caption_column, image_column, train_transforms, concept_overwrite: Optional[str] = None):
    '''
    Adapted from The HuggingFace Inc. team. All rights reserved.
    Licensed under the Apache License, Version 2.0.
    Source: https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py

    concept_overwrite: concept to be used for overwriting, described as an textual string (used to modify the prompt).
    TODO: this handling of concept_overwrite is weird... I wish this were somewhat more structured/organized/clear
    '''
    images = [image.convert("RGB") for image in examples[image_column]]
    examples["pixel_values"] = [train_transforms(image) for image in images]
    examples["input_ids"] = tokenize_captions(examples, tokenizer, caption_column)
    if concept_overwrite:
        examples["forget_ids"] = forget_tokens(examples, tokenizer, caption_column, "an image of garbage_truck")  # TODO hardcoded
    return examples


def collate_fn(examples):
    '''
    Adapted from The HuggingFace Inc. team. All rights reserved.
    Licensed under the Apache License, Version 2.0.
    Source: https://github.com/huggingface/diffusers/blob/main/examples/text_to_image/train_text_to_image_lora.py
    '''
    pixel_values = torch.stack([example["pixel_values"] for example in examples])
    pixel_values = pixel_values.to(memory_format=torch.contiguous_format).float()
    input_ids = torch.stack([example["input_ids"] for example in examples])
    result = {"pixel_values": pixel_values, "input_ids": input_ids}
    if "forget_ids" in examples[0]:
        # This happens when `preprocess_train` was called with a non-none `concept_overwrite`
        result["forget_ids"] = torch.stack([example["forget_ids"] for example in examples])
    return result


def launch_accelerated_training(unlearner: 'Unlearner'):  # type: ignore
    '''
    Wrap your training function with the accelerator
    '''
    accelerator = Accelerator(mixed_precision="fp16", dynamo_backend="no")
    with accelerator.local_main_process_first():
        if accelerator.is_local_main_process:
            unlearner.train()

    accelerator.wait_for_everyone()  # Wait for all processes to finish
