import streamlit as st
from models import Funcionario
from extensions import database as db
from flask import Flask
from datetime import datetime
from sqlalchemy.orm import scoped_session
