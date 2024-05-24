import torch
from torch import nn, Tensor
import numpy as np


class myMAE(nn.L1Loss):
    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        return super().forward(input[:,0:1], target) #for now : hardcoded only on first filter 
