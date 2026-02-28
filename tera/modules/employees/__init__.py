"""Employees module package.

This module provides employee profile management functionality, abstracting
employee data handling from the payroll module for better separation of concerns.
The module manages employee profiles, personal information, employment details,
and compensation data.
"""
from . import setup  # expose setup for modules.fix invocation
from .service import EmployeeService  # expose service contract for other modules

__all__ = ["setup", "EmployeeService"]
