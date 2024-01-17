class NewsDatabaseRouter:
    def db_for_read(self, model, **hints):
        if model._meta.app_label == 'news':
            return 'dj30'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label == 'news':
            return 'dj30'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label == 'news' or
            obj2._meta.app_label == 'news'
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if db == 'dj30':
            return app_label == 'news'
        elif app_label == 'news':
            return False
        return None