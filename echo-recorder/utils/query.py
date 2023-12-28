# -*- coding=utf-8
class Criteria:
    def __init__(self, key: str, chain: list['Criteria'] = None):
        self.key: str = key
        self.value: any = None
        self.chain: list[Criteria] = chain if chain else []
        self.chain.append(self)
        self.criteria: dict[str, any] = {}

    @staticmethod
    def where(key: str) -> 'Criteria':
        return Criteria(key=key)

    def and_(self, key: str) -> 'Criteria':
        return Criteria(key=key, chain=self.chain)

    def eq(self, value: any) -> 'Criteria':
        self.value = value
        return self

    def is_null(self) -> 'Criteria':
        self.value = None
        return self

    def is_empty(self) -> 'Criteria':
        self.criteria["$isempty"] = True
        return self

    def is_blank(self) -> 'Criteria':
        self.criteria["$isblank"] = True
        return self

    def ne(self, value: any) -> 'Criteria':
        self.criteria["$ne"] = value
        return self

    def not_eq(self, value: any) -> 'Criteria':
        return self.ne(value)

    def not_(self, value: any) -> 'Criteria':
        self.criteria["$not"] = value
        return self

    def regex(self, regex: str) -> 'Criteria':
        self.criteria["$regex"] = regex
        return self

    def like(self, value: any) -> 'Criteria':
        self.criteria["$like"] = value
        return self

    def startswith(self, value: any) -> 'Criteria':
        self.criteria["$startswith"] = value
        return self

    def endswith(self, value: any) -> 'Criteria':
        self.criteria["$endswith"] = value
        return self

    def lt(self, value: any) -> 'Criteria':
        self.criteria["$lt"] = value
        return self

    def lte(self, value: any) -> 'Criteria':
        self.criteria["$lte"] = value
        return self

    def gt(self, value: any) -> 'Criteria':
        self.criteria["$gt"] = value
        return self

    def gte(self, value: any) -> 'Criteria':
        self.criteria["$gte"] = value
        return self

    def between(self, start, end) -> 'Criteria':
        self.criteria["$between"] = (start, end)
        return self

    def in_(self, values: list[any]) -> 'Criteria':
        self.criteria["$in"] = values
        return self

    def nin(self, values: list[any]) -> 'Criteria':
        self.criteria["$nin"] = values
        return self

    def not_in(self, values: list[any]) -> 'Criteria':
        return self.nin(values)

    def any(self, values: list[any]) -> 'Criteria':
        return self.in_(values)

    def all(self, values: list[any]) -> 'Criteria':
        self.criteria["$all"] = values
        return self
