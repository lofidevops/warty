from dataclasses import dataclass

from wartlib.environment import Environment


@dataclass
class HelloEnvironment(Environment):
    CANONICAL_EMAIL = ""


print("Hello world.")

E = HelloEnvironment()
E.set_environment()
E.validate()
print(E.CANONICAL_EMAIL)
