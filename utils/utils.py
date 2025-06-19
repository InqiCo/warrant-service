import re


def clear_tax_id(valor):
    """Remove pontos, traços e barras de um CPF ou CNPJ usando regex."""
    return re.sub(r'[.\-\/]', '', str(valor))
