import wpf
import clr

clr.AddReference("PresentationCore")  
clr.AddReference("PresentationFramework")  
clr.AddReference("WindowsBase")

from System.Windows.Markup import XamlReader
from System.Windows import Application, Window
from System.ComponentModel import INotifyPropertyChanged, PropertyChangedEventArgs

from exceptions import ValueError

import System
import pyevent
import clrtype


class notify_property(property):

    def __init__(self, getter):
        def newgetter(slf):
            try:
                return getter(slf)
            except AttributeError:
                return None
        super(notify_property, self).__init__(newgetter)

    def setter(self, setter):
        def newsetter(slf, newvalue):
            oldvalue = self.fget(slf)
            if oldvalue != newvalue:
                setter(slf, newvalue)
                slf.OnPropertyChanged(setter.__name__)
        return property(
            fget=self.fget,
            fset=newsetter,
            fdel=self.fdel,
            doc=self.__doc__)
    

class NotifyPropertyChangedBase(INotifyPropertyChanged):
    PropertyChanged = None

    def __init__(self):
        self.PropertyChanged, self._propertyChangedCaller = pyevent.make_event()

    def add_PropertyChanged(self, value):
        self.PropertyChanged += value

    def remove_PropertyChanged(self, value):
        self.PropertyChanged -= value

    def OnPropertyChanged(self, propertyName):
        if self.PropertyChanged is not None:
            self._propertyChangedCaller(self, PropertyChangedEventArgs(propertyName))


class ViewModel(NotifyPropertyChangedBase):

    def __init__(self, model):
        super(ViewModel, self).__init__()
        self._model = model
        self._CelsiusValue = ''
        self._FahrenheitValue = ''
        self._CelsiusFocus = False

    def swap_focus(self, sender, e):
        self._CelsiusFocus = not self._CelsiusFocus
                
    @notify_property
    def CelsiusValue(self):
        return self._CelsiusValue

    @CelsiusValue.setter
    def CelsiusValue(self, value):
        if self._CelsiusFocus:
            self._CelsiusValue = value
            self.FahrenheitValue = self._model.convert_celsius_to_fahrenheit(self._CelsiusValue)
        else:
            self._CelsiusValue = value

    @notify_property
    def FahrenheitValue(self):
        return self._FahrenheitValue

    @FahrenheitValue.setter
    def FahrenheitValue(self, value):
        if not self._CelsiusFocus:
            self._FahrenheitValue = value
            self.CelsiusValue = self._model.convert_fahrenheit_to_celsius(self._FahrenheitValue)
        else:
            self._FahrenheitValue = value


class Model():
    def convert_celsius_to_fahrenheit(self, celsius):
        try:
            return str((float(celsius) * 9/5) + 32)
        except ValueError:
            return ''
    
    def convert_fahrenheit_to_celsius(self, fahrenheit):
        try:
            return str((float(fahrenheit) - 32) * 5/9)
        except ValueError:
            return ''


class MyWindow(Window):
    def __init__(self):
        wpf.LoadComponent(self, 'CelsiusConverter.xaml')
        model = Model()
        viewModel = ViewModel(model)
        self.DataContext = viewModel
        self._CelsiusBox.GotKeyboardFocus += viewModel.swap_focus
        self._FahrenheitBox.GotKeyboardFocus += viewModel.swap_focus

    @property
    def FahrenheitBox(self):
        return self._FahrenheitBox

    @FahrenheitBox.setter
    def FahrenheitBox(self, value):
        self._FahrenheitBox = value

    @property
    def CelsiusBox(self):
        return self._CelsiusBox

    @CelsiusBox.setter
    def CelsiusBox(self, value):
        self._CelsiusBox = value


if __name__ == '__main__':
    Application().Run(MyWindow())
