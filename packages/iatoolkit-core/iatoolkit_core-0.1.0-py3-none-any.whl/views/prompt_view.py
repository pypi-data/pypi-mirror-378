# Copyright (c) 2024 Fernando Libedinsky
# Producto: IAToolkit
# Todos los derechos reservados.
# En trámite de registro en el Registro de Propiedad Intelectual de Chile.

from flask import request, jsonify, render_template
from flask.views import MethodView
from services.prompt_manager_service import PromptService
from auth import IAuthentication
from injector import inject
import logging


class PromptView(MethodView):
    @inject
    def __init__(self,
                 iauthentication: IAuthentication,
                 prompt_service: PromptService ):
        self.iauthentication = iauthentication
        self.prompt_service = prompt_service

    def get(self, company_short_name):
        # get access credentials
        iaut = self.iauthentication.verify(company_short_name)
        if not iaut.get("success"):
            return jsonify(iaut), 401

        try:
            response = self.prompt_service.get_user_prompts(company_short_name)
            if "error" in response:
                return {'error_message': response["error"]}, 402

            return response, 200
        except Exception as e:
            logging.exception(
                f"Error inesperado al obtener el historial de consultas para company {company_short_name}: {e}")
            return jsonify({"error_message": str(e)}), 500
