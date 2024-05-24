import torch
from torch import nn, Tensor
import numpy as np


class myMSE(nn.MSELoss):
    def forward(self, input: Tensor, target: Tensor) -> Tensor:
        return super().forward(input[:,0:1], target) #for now : hardcoded only on first filter 
