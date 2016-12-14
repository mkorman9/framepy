from framepy import db


def mock_logic(logic_class, context):
    class FakeTransactionContextManager(object):
        def __init__(self):
            pass

        def __enter__(self):
            return None

        def __exit__(self, exc_type, exc_val, exc_tb):
            pass

    target = logic_class()
    setattr(target, 'context', context)
    db.transaction = lambda _: FakeTransactionContextManager()
    return target
