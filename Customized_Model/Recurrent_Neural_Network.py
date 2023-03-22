from tqdm import tqdm
import torch.nn as nn
import numpy as np
import torch


class RNN(nn.Module):
    def __init__(self, input_dim, output_dim, num_hidden=1, solver="adam", batch_size=200,learning_rate=0.001, epoch=100):
        super(RNN, self).__init__()
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.hidden_dim = int((self.input_dim + self.output_dim) * 2 / 3)
        self.num_hidden = num_hidden

        self.solver = solver
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.epoch = epoch

        self.model = nn.ModuleList()
        self.model.append(nn.RNN(self.input_dim, self.hidden_dim, batch_first=True))
        if self.num_hidden != 1:
            for i in range(self.num_hidden-1):
                self.model.append(nn.RNN(self.hidden_dim, self.hidden_dim, batch_first=True))
        self.model.append(torch.nn.Linear(self.hidden_dim, self.output_dim))

    def forward(self, x, h):
        for i, l in enumerate(self.model):
            if i != len(self.model):
                out, h[i] = self.rnn_layers[i](x, h[i])
                x = out
            else:
                x = self.model[i](x)
        return x, h

    def fit(self, x, y):
        criterion = nn.MSELoss()
        if self.solver == "adam":
            optimizer = torch.optim.Adam(self.parameters(), lr=self.learning_rate)
        elif self.solver == "adadelta":
            optimizer = torch.optim.Adadelta(self.parameters(), lr=self.learning_rate)
        elif self.solver == "nadam":
            optimizer = torch.optim.NAdam(self.parameters(), lr=self.learning_rate)
        for epoch in tqdm(range(self.epoch)):
            loss_list = []
            for i in range(0, len(x), self.batch_size):
                inputs = torch.autograd.Variable(torch.Tensor(x[i:i+self.batch_size]))
                targets = torch.autograd.Variable(torch.Tensor(y[i:i+self.batch_size]))
                optimizer.zero_grad()
                outputs = self(inputs)
                loss = criterion(outputs, targets)
                loss.backward()
                optimizer.step()
                loss_list.append(loss.item())

            if (epoch + 1) % 10 == 0:
                print('Epoch [%d/%d], Loss: %.4f' % (epoch + 1, self.epoch, np.mean(loss_list)))

    def predict(self, x):
        with torch.no_grad():
            inputs = torch.tensor(x).float()
            outputs = self(inputs)
        return np.array(outputs)






