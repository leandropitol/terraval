#!/usr/bin/env bash
set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}🌾  Instalando TerraVal...${NC}"
echo ""

# Verificar Python
if command -v python3 &>/dev/null; then
    PYTHON=python3
elif command -v python &>/dev/null; then
    PYTHON=python
else
    echo -e "${RED}❌  Python não encontrado. Instale Python 3.10+ e tente novamente.${NC}"
    echo "   https://www.python.org/downloads/"
    exit 1
fi

PY_MINOR=$($PYTHON -c 'import sys; print(sys.version_info.minor)')
PY_MAJOR=$($PYTHON -c 'import sys; print(sys.version_info.major)')

if [ "$PY_MAJOR" -lt "3" ] || [ "$PY_MINOR" -lt "10" ]; then
    echo -e "${RED}❌  Python 3.10+ necessário. Versão encontrada: $($PYTHON --version)${NC}"
    exit 1
fi

echo -e "   Python $($PYTHON --version) encontrado ✓"
echo ""

# Instalar
if command -v uv &>/dev/null; then
    echo -e "${YELLOW}📦  Instalando via uv...${NC}"
    uv pip install git+https://github.com/leandropitol/terraval.git
else
    echo -e "${YELLOW}📦  Instalando via pip...${NC}"
    $PYTHON -m pip install git+https://github.com/leandropitol/terraval.git
fi

echo ""
echo -e "${GREEN}✅  TerraVal instalado com sucesso!${NC}"
echo ""
echo -e "   Configurar:  ${YELLOW}terraval setup${NC}"
echo -e "   Iniciar:     ${YELLOW}terraval${NC}"
echo ""
