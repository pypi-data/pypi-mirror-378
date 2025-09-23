# src/iatoolkit/toolkit_config.py
from injector import Module, Binder, singleton
from flask import Flask
from repositories.database_manager import DatabaseManager

class IAToolkitConfig(Module):
    def __init__(self, app: Flask, db_manager: DatabaseManager):
        self.app = app
        self.db_manager = db_manager

    def configure(self, binder: Binder):
        binder.bind(Flask, to=self.app, scope=singleton)
        binder.bind(DatabaseManager, to=self.db_manager, scope=singleton)