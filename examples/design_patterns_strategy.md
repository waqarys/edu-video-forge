# Design Patterns — Strategy Pattern

## Scene: slides
**Narration:** The Strategy pattern lets you define a family of algorithms, encapsulate each one, and make them interchangeable.
**Content:**
Strategy Pattern

- Encapsulate algorithms
- Interchangeable at runtime
- Open/Closed Principle

## Scene: class-diagram
**Narration:** Here is the classic UML class diagram for the Strategy pattern. Context holds a reference to the Strategy interface, and concrete strategies implement the behavior.
**Content:**
Context uses Strategy
ConcreteStrategyA and ConcreteStrategyB implement Strategy

## Scene: code
**Narration:** In code, the Context delegates to the current strategy. You can swap strategies without changing the Context.
**Content:**
```python
class Strategy:
    def execute(self):
        pass

class ConcreteA(Strategy):
    def execute(self):
        return "Algorithm A"

class Context:
    def __init__(self, strategy: Strategy):
        self.strategy = strategy

    def do_work(self):
        return self.strategy.execute()
```

## Scene: sequence
**Narration:** At runtime the client sets a strategy and the Context calls execute on it.
**Content:**
Client sets ConcreteA
Context calls execute

## Scene: slides
**Narration:** This is one of the most useful patterns when you have multiple ways to perform the same task and want to avoid long if-else chains.
**Content:**
When to Use Strategy

- Multiple algorithms for one task
- Runtime selection
- Avoid conditional complexity
