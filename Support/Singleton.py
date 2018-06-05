class Singleton:
    def __init__(self,decorated):
        self._decorated = decorated

    def inst(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self, *args, **kwargs):
        raise TypeError("Singletons must be accesed through 'inst()'")

    def __instancecheck__(self, instance):
        return isinstance(instance,self._decorated)