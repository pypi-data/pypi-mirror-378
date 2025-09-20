# Copyright (c) 2024 Fernando Libedinsky
# Producto: IAToolkit
# Todos los derechos reservados.
# En trámite de registro en el Registro de Propiedad Intelectual de Chile.

from sqlalchemy import Column, Integer, String, DateTime, Enum, Text, JSON, Boolean, ForeignKey, Table
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import relationship, class_mapper, declarative_base
from datetime import datetime
from pgvector.sqlalchemy import Vector
from enum import Enum as PyEnum
import secrets
import enum


# Definir la base para el ORM
class Base(DeclarativeBase):
    pass

# Tabla de relación muchos a muchos entre User y Company
user_company = Table('user_company',
                     Base.metadata,
                    Column('user_id', Integer,
                           ForeignKey('users.id', ondelete='CASCADE'),
                                primary_key=True),
                     Column('company_id', Integer,
                            ForeignKey('companies.id',ondelete='CASCADE'),
                                primary_key=True),
                     Column('is_active', Boolean, default=True),
                     Column('role', String(50), default='user'),  # Para manejar roles por empresa
                     Column('created_at', DateTime, default=datetime.now)
                     )

class ApiKey(Base):
    __tablename__ = 'api_keys'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    key = Column(String(128), unique=True, nullable=False, index=True) # La API Key en sí
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    last_used_at = Column(DateTime, nullable=True) # Opcional: para rastrear uso

    company = relationship("Company", back_populates="api_keys")


class Company(Base):
    __tablename__ = 'companies'

    id = Column(Integer, primary_key=True)
    name = Column(String(256), nullable=False)
    short_name = Column(String(20), nullable=False, default='')

    # encrypted api-key
    llm_api_key = Column(String, nullable=True)

    logo_file = Column(String(128), nullable=True, default='')
    parameters = Column(JSON, nullable=True, default={})
    created_at = Column(DateTime, default=datetime.now)
    allow_jwt = Column(Boolean, default=False, nullable=True)

    documents = relationship("Document",
                             back_populates="company",
                             cascade="all, delete-orphan",
                             lazy='dynamic')
    functions = relationship("Function",
                           back_populates="company",
                           cascade="all, delete-orphan")
    vsdocs = relationship("VSDoc",
                          back_populates="company",
                          cascade="all, delete-orphan")
    llm_queries = relationship("LLMQuery",
                               back_populates="company",
                               cascade="all, delete-orphan")
    users = relationship("User",
                         secondary=user_company,
                         back_populates="companies")
    api_keys = relationship("ApiKey",
                            back_populates="company",
                            cascade="all, delete-orphan")

    tasks = relationship("Task", back_populates="company")
    feedbacks = relationship("UserFeedback",
                               back_populates="company",
                               cascade="all, delete-orphan")
    prompts = relationship("Prompt",
                             back_populates="company",
                             cascade="all, delete-orphan")

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

# users with rights to use this app
class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    email = Column(String(80), unique=True, nullable=False)
    rut= Column(String(20), unique=True, nullable=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    password = Column(String, nullable=False)
    verified = Column(Boolean, nullable=False, default=False)
    verification_url = Column(String, nullable=True)
    temp_code = Column(String, nullable=True)
    super_user = Column(Boolean, nullable=True, default=False)

    companies = relationship(
        "Company",
        secondary=user_company,
        back_populates="users",
        cascade="all",
        passive_deletes=True,
        lazy='dynamic'
    )

    def to_dict(self):
        return {
            'id': self.id,
            'email': self.email,
            'rut': self.rut,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'created_at': str(self.created_at),
            'verified': self.verified,
            'super_user': self.super_user,
            'companies': [company.to_dict() for company in self.companies]
        }

class Function(Base):
    __tablename__ = 'functions'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer,
                        ForeignKey('companies.id',ondelete='CASCADE'),
                        nullable=True)
    name = Column(String(255), nullable=False)
    system_function = Column(Boolean, default=False)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.now)

    company = relationship('Company', back_populates='functions')

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}


class Document(Base):
    __tablename__ = 'documents'

    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, ForeignKey('companies.id',
                    ondelete='CASCADE'), nullable=False)
    filename = Column(String(256), nullable=False, index=True)
    content = Column(Text, nullable=False)
    content_b64 = Column(Text, nullable=False)
    meta = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.now)

    company = relationship("Company", back_populates="documents")

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

# Tabla de tipos de documento
class DocumentType(Base):
    __tablename__ = 'document_types'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(128), unique=True, nullable=False)  # identificador de documento
    description = Column(String(512), nullable=True)               # Ejemplo: "Contrato de Prenda"
    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

# all the user queries
class LLMQuery(Base):
    __tablename__ = 'llm_queries'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id',
                            ondelete='CASCADE'), nullable=False)
    user_identifier = Column(String(128), nullable=False)
    task_id = Column(Integer, default=0, nullable=True)
    query = Column(Text, nullable=False)
    output = Column(Text, nullable=False)
    response = Column(JSON, nullable=True, default={})
    valid_response = Column(Boolean, nullable=False, default=False)
    function_calls = Column(JSON, nullable=True, default={})
    stats = Column(JSON, default={})
    answer_time = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.now)

    company = relationship("Company", back_populates="llm_queries")
    tasks = relationship("Task", back_populates="llm_query")

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}


class VSDoc(Base):
    __tablename__ = "vsdocs"

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id',
                    ondelete='CASCADE'), nullable=False)
    document_id = Column(Integer, ForeignKey('documents.id',
                        ondelete='CASCADE'), nullable=False)
    text = Column(Text, nullable=False)
    embedding = Column(Vector(384), nullable=False)  # Ajusta la dimensión si es necesario

    company = relationship("Company", back_populates="vsdocs")

    def to_dict(self):
        return {column.key: getattr(self, column.key) for column in class_mapper(self.__class__).columns}

class TaskStatus(PyEnum):
    pendiente = "pendiente"  # Tarea creada y en espera de ejecución.
    ejecutado = "ejecutado"  # La IA ya procesó la tarea (resultado en llm_query).
    aprobada = "aprobada"  # Validada y aprobada por humano.
    rechazada = "rechazada"  # Validada y rechazada por humano.
    fallida = "fallida"  # Error durante la ejecución.

class TaskType(Base):
    __tablename__ = 'task_types'

    id = Column(Integer, primary_key=True)
    name = Column(String(100), unique=True, nullable=False)
    prompt_template = Column(String(100), nullable=True)  # Plantilla de prompt por defecto.
    template_args = Column(JSON, nullable=True)  # Argumentos/prefijos de configuración para el template.

class Task(Base):
    __tablename__ = 'tasks'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))

    user_id = Column(Integer, nullable=True, default=0)
    task_type_id = Column(Integer, ForeignKey('task_types.id'), nullable=False)
    status = Column(Enum(TaskStatus, name="task_status_enum"),
                    default=TaskStatus.pendiente, nullable=False)
    client_data = Column(JSON, nullable=True, default={})
    company_task_id = Column(Integer, nullable=True, default=0)
    execute_at = Column(DateTime, default=datetime.now, nullable=True)
    llm_query_id = Column(Integer, ForeignKey('llm_queries.id'), nullable=True)
    callback_url = Column(String(512), default=None, nullable=True)
    files = Column(JSON, default=[], nullable=True)

    review_user = Column(String(128), nullable=True, default='')
    review_date = Column(DateTime, nullable=True)
    comment = Column(Text, nullable=True)
    approved = Column(Boolean, nullable=False, default=False)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)

    task_type = relationship("TaskType")
    llm_query = relationship("LLMQuery", back_populates="tasks", uselist=False)
    company = relationship("Company", back_populates="tasks")

class UserFeedback(Base):
    __tablename__ = 'feedback'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id',
                                            ondelete='CASCADE'), nullable=False)
    local_user_id = Column(Integer, default=0, nullable=True)
    external_user_id = Column(String(128), default='', nullable=True)
    message = Column(Text, nullable=False)
    rating = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.now)

    company = relationship("Company", back_populates="feedbacks")


class PromptCategory(Base):
    __tablename__ = 'prompt_categories'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    order = Column(Integer, nullable=False, default=0)
    company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)

    prompts = relationship("Prompt", back_populates="category", order_by="Prompt.order")

    def __repr__(self):
        return f"<PromptCategory(name='{self.name}', order={self.order})>"


class Prompt(Base):
    __tablename__ = 'prompt'

    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey('companies.id',
                                            ondelete='CASCADE'), nullable=True)
    name = Column(String(64), nullable=False)
    description = Column(String(256), nullable=False)
    filepath = Column(String(256), nullable=False)
    active = Column(Boolean, default=True)
    is_system_prompt = Column(Boolean, default=False)
    order = Column(Integer, nullable=False, default=0)  # Nuevo campo para el orden
    category_id = Column(Integer, ForeignKey('prompt_categories.id'), nullable=True)
    parameters = Column(JSON, nullable=True, default={})

    created_at = Column(DateTime, default=datetime.now)

    company = relationship("Company", back_populates="prompts")
    category = relationship("PromptCategory", back_populates="prompts")
