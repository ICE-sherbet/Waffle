from abc import ABCMeta, abstractmethod

class absTextBoxCall(metaclass=ABCMeta):
    @abstractmethod
    def textboxPressCall(self,event):
        pass 
    
    @abstractmethod
    def textboxReleaseCall(self,event):
        pass

    @abstractmethod
    def textBoxEnter(self,event):
        pass
    @abstractmethod
    def textBoxKey(self,event):
        pass