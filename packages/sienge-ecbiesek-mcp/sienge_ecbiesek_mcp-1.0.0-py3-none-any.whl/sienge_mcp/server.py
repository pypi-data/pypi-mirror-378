#!/usr/bin/env python3
"""
SIENGE MCP COMPLETO - FastMCP com Autenticação Flexível
Suporta Bearer Token e Basic Auth
"""

from fastmcp import FastMCP
import httpx
import asyncio
from typing import Dict, List, Optional, Any
import json
import os
from dotenv import load_dotenv
from datetime import datetime
import base64

# Carrega as variáveis de ambiente
load_dotenv()

mcp = FastMCP("Sienge API Integration 🏗️")

# Configurações da API do Sienge
SIENGE_BASE_URL = os.getenv("SIENGE_BASE_URL", "https://api.sienge.com.br")
SIENGE_SUBDOMAIN = os.getenv("SIENGE_SUBDOMAIN", "")
SIENGE_USERNAME = os.getenv("SIENGE_USERNAME", "")
SIENGE_PASSWORD = os.getenv("SIENGE_PASSWORD", "")
SIENGE_API_KEY = os.getenv("SIENGE_API_KEY", "")
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))

class SiengeAPIError(Exception):
    """Exceção customizada para erros da API do Sienge"""
    pass

async def make_sienge_request(method: str, endpoint: str, params: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict:
    """
    Função auxiliar para fazer requisições à API do Sienge
    Suporta tanto Bearer Token quanto Basic Auth
    """
    try:
        async with httpx.AsyncClient(timeout=REQUEST_TIMEOUT) as client:
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            # Configurar autenticação e URL
            auth = None
            
            if SIENGE_API_KEY and SIENGE_API_KEY != "sua_api_key_aqui":
                # Bearer Token (Recomendado)
                headers["Authorization"] = f"Bearer {SIENGE_API_KEY}"
                url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/v1{endpoint}"
            elif SIENGE_USERNAME and SIENGE_PASSWORD:
                # Basic Auth usando httpx.BasicAuth
                auth = httpx.BasicAuth(SIENGE_USERNAME, SIENGE_PASSWORD)
                url = f"{SIENGE_BASE_URL}/{SIENGE_SUBDOMAIN}/public/api/v1{endpoint}"
            else:
                return {
                    "success": False,
                    "error": "No Authentication",
                    "message": "Configure SIENGE_API_KEY ou SIENGE_USERNAME/PASSWORD no .env"
                }
            
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=json_data,
                auth=auth
            )
            
            if response.status_code in [200, 201]:
                try:
                    return {
                        "success": True,
                        "data": response.json(),
                        "status_code": response.status_code
                    }
                except:
                    return {
                        "success": True,
                        "data": {"message": "Success"},
                        "status_code": response.status_code
                    }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "message": response.text,
                    "status_code": response.status_code
                }
                
    except httpx.TimeoutException:
        return {
            "success": False,
            "error": "Timeout",
            "message": f"A requisição excedeu o tempo limite de {REQUEST_TIMEOUT}s"
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": f"Erro na requisição: {str(e)}"
        }

# ============ CONEXÃO E TESTE ============

@mcp.tool
async def test_sienge_connection() -> Dict:
    """Testa a conexão com a API do Sienge"""
    try:
        # Tentar endpoint mais simples primeiro
        result = await make_sienge_request("GET", "/customer-types")
        
        if result["success"]:
            auth_method = "Bearer Token" if SIENGE_API_KEY else "Basic Auth"
            return {
                "success": True,
                "message": "✅ Conexão com API do Sienge estabelecida com sucesso!",
                "api_status": "Online",
                "auth_method": auth_method,
                "timestamp": datetime.now().isoformat()
            }
        else:
            return {
                "success": False,
                "message": "❌ Falha ao conectar com API do Sienge",
                "error": result.get("error"),
                "details": result.get("message"),
                "timestamp": datetime.now().isoformat()
            }
    except Exception as e:
        return {
            "success": False,
            "message": "❌ Erro ao testar conexão",
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

# ============ CLIENTES ============

@mcp.tool
async def get_sienge_customers(limit: Optional[int] = 50, offset: Optional[int] = 0, search: Optional[str] = None, customer_type_id: Optional[str] = None) -> Dict:
    """
    Busca clientes no Sienge com filtros
    
    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
        search: Buscar por nome ou documento
        customer_type_id: Filtrar por tipo de cliente
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    
    if search:
        params["search"] = search
    if customer_type_id:
        params["customer_type_id"] = customer_type_id
    
    result = await make_sienge_request("GET", "/customers", params=params)
    
    if result["success"]:
        data = result["data"]
        customers = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(customers))
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(customers)} clientes (total: {total_count})",
            "customers": customers,
            "count": len(customers),
            "filters_applied": params
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar clientes",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_customer_types() -> Dict:
    """Lista tipos de clientes disponíveis"""
    result = await make_sienge_request("GET", "/customer-types")
    
    if result["success"]:
        data = result["data"]
        customer_types = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(customer_types))
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(customer_types)} tipos de clientes (total: {total_count})",
            "customer_types": customer_types,
            "count": len(customer_types)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar tipos de clientes",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ CREDORES ============

@mcp.tool
async def get_sienge_creditors(limit: Optional[int] = 50, offset: Optional[int] = 0, search: Optional[str] = None) -> Dict:
    """
    Busca credores/fornecedores
    
    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
        search: Buscar por nome
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    if search:
        params["search"] = search
    
    result = await make_sienge_request("GET", "/creditors", params=params)
    
    if result["success"]:
        data = result["data"]
        creditors = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(creditors))
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(creditors)} credores (total: {total_count})",
            "creditors": creditors,
            "count": len(creditors)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar credores",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_creditor_bank_info(creditor_id: str) -> Dict:
    """
    Consulta informações bancárias de um credor
    
    Args:
        creditor_id: ID do credor (obrigatório)
    """
    result = await make_sienge_request("GET", f"/creditors/{creditor_id}/bank-informations")
    
    if result["success"]:
        return {
            "success": True,
            "message": f"✅ Informações bancárias do credor {creditor_id}",
            "creditor_id": creditor_id,
            "bank_info": result["data"]
        }
    
    return {
        "success": False,
        "message": f"❌ Erro ao buscar info bancária do credor {creditor_id}",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ FINANCEIRO ============

@mcp.tool
async def get_sienge_accounts_receivable(customer_id: Optional[str] = None, due_date_from: Optional[str] = None, 
                                       due_date_to: Optional[str] = None, status: Optional[str] = None, limit: Optional[int] = 50) -> Dict:
    """
    Consulta títulos a receber
    
    Args:
        customer_id: ID do cliente
        due_date_from: Data inicial (YYYY-MM-DD)
        due_date_to: Data final (YYYY-MM-DD)
        status: Status (open, paid, overdue)
        limit: Máximo de registros
    """
    params = {"limit": min(limit or 50, 200)}
    
    if customer_id:
        params["customer_id"] = customer_id
    if due_date_from:
        params["due_date_from"] = due_date_from
    if due_date_to:
        params["due_date_to"] = due_date_to
    if status:
        params["status"] = status
    
    result = await make_sienge_request("GET", "/accounts-receivable", params=params)
    
    if result["success"]:
        data = result["data"]
        receivables = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(receivables)} títulos a receber",
            "receivables": receivables,
            "count": len(receivables),
            "filters": params
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar títulos a receber",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_bills(start_date: Optional[str] = None, end_date: Optional[str] = None, 
                          creditor_id: Optional[str] = None, status: Optional[str] = None, 
                          limit: Optional[int] = 50) -> Dict:
    """
    Consulta títulos a pagar (contas a pagar) - REQUER startDate obrigatório
    
    Args:
        start_date: Data inicial obrigatória (YYYY-MM-DD) - padrão últimos 30 dias
        end_date: Data final (YYYY-MM-DD) - padrão hoje
        creditor_id: ID do credor
        status: Status do título (ex: open, paid, cancelled)
        limit: Máximo de registros (padrão: 50, máx: 200)
    """
    from datetime import datetime, timedelta
    
    # Se start_date não fornecido, usar últimos 30 dias
    if not start_date:
        start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    # Se end_date não fornecido, usar hoje
    if not end_date:
        end_date = datetime.now().strftime('%Y-%m-%d')
    
    # Parâmetros obrigatórios
    params = {
        "startDate": start_date,  # OBRIGATÓRIO pela API
        "endDate": end_date,
        "limit": min(limit or 50, 200)
    }
    
    # Parâmetros opcionais
    if creditor_id:
        params["creditor_id"] = creditor_id
    if status:
        params["status"] = status
    
    result = await make_sienge_request("GET", "/bills", params=params)
    
    if result["success"]:
        data = result["data"]
        bills = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(bills))
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(bills)} títulos a pagar (total: {total_count}) - período: {start_date} a {end_date}",
            "bills": bills,
            "count": len(bills),
            "total_count": total_count,
            "period": {"start_date": start_date, "end_date": end_date},
            "filters": params
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar títulos a pagar",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ COMPRAS ============

@mcp.tool
async def get_sienge_purchase_orders(purchase_order_id: Optional[str] = None, status: Optional[str] = None,
                                   date_from: Optional[str] = None, limit: Optional[int] = 50) -> Dict:
    """
    Consulta pedidos de compra
    
    Args:
        purchase_order_id: ID específico do pedido
        status: Status do pedido
        date_from: Data inicial (YYYY-MM-DD)
        limit: Máximo de registros
    """
    if purchase_order_id:
        result = await make_sienge_request("GET", f"/purchase-orders/{purchase_order_id}")
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Pedido {purchase_order_id} encontrado",
                "purchase_order": result["data"]
            }
        return result
    
    params = {"limit": min(limit or 50, 200)}
    if status:
        params["status"] = status
    if date_from:
        params["date_from"] = date_from
    
    result = await make_sienge_request("GET", "/purchase-orders", params=params)
    
    if result["success"]:
        data = result["data"]
        orders = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(orders)} pedidos de compra",
            "purchase_orders": orders,
            "count": len(orders)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar pedidos de compra",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_purchase_order_items(purchase_order_id: str) -> Dict:
    """
    Consulta itens de um pedido de compra específico
    
    Args:
        purchase_order_id: ID do pedido (obrigatório)
    """
    result = await make_sienge_request("GET", f"/purchase-orders/{purchase_order_id}/items")
    
    if result["success"]:
        data = result["data"]
        items = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(items)} itens no pedido {purchase_order_id}",
            "purchase_order_id": purchase_order_id,
            "items": items,
            "count": len(items)
        }
    
    return {
        "success": False,
        "message": f"❌ Erro ao buscar itens do pedido {purchase_order_id}",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_purchase_requests(purchase_request_id: Optional[str] = None, limit: Optional[int] = 50) -> Dict:
    """
    Consulta solicitações de compra
    
    Args:
        purchase_request_id: ID específico da solicitação
        limit: Máximo de registros
    """
    if purchase_request_id:
        result = await make_sienge_request("GET", f"/purchase-requests/{purchase_request_id}")
        if result["success"]:
            return {
                "success": True,
                "message": f"✅ Solicitação {purchase_request_id} encontrada",
                "purchase_request": result["data"]
            }
        return result
    
    params = {"limit": min(limit or 50, 200)}
    result = await make_sienge_request("GET", "/purchase-requests", params=params)
    
    if result["success"]:
        data = result["data"]
        requests = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontradas {len(requests)} solicitações de compra",
            "purchase_requests": requests,
            "count": len(requests)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar solicitações de compra",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def create_sienge_purchase_request(description: str, project_id: str, items: List[Dict[str, Any]]) -> Dict:
    """
    Cria nova solicitação de compra
    
    Args:
        description: Descrição da solicitação
        project_id: ID do projeto/obra
        items: Lista de itens da solicitação
    """
    request_data = {
        "description": description,
        "project_id": project_id,
        "items": items,
        "date": datetime.now().strftime("%Y-%m-%d")
    }
    
    result = await make_sienge_request("POST", "/purchase-requests", json_data=request_data)
    
    if result["success"]:
        return {
            "success": True,
            "message": "✅ Solicitação de compra criada com sucesso",
            "request_id": result["data"].get("id"),
            "data": result["data"]
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao criar solicitação de compra",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ ESTOQUE ============

@mcp.tool
async def get_sienge_stock_inventory(cost_center_id: str, resource_id: Optional[str] = None) -> Dict:
    """
    Consulta inventário de estoque por centro de custo
    
    Args:
        cost_center_id: ID do centro de custo (obrigatório)
        resource_id: ID do insumo específico (opcional)
    """
    if resource_id:
        endpoint = f"/stock-inventories/{cost_center_id}/items/{resource_id}"
    else:
        endpoint = f"/stock-inventories/{cost_center_id}/items"
    
    result = await make_sienge_request("GET", endpoint)
    
    if result["success"]:
        data = result["data"]
        items = data.get("results", []) if isinstance(data, dict) else data
        count = len(items) if isinstance(items, list) else 1
        
        return {
            "success": True,
            "message": f"✅ Inventário do centro de custo {cost_center_id}",
            "cost_center_id": cost_center_id,
            "inventory": items,
            "count": count
        }
    
    return {
        "success": False,
        "message": f"❌ Erro ao consultar estoque do centro {cost_center_id}",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_stock_reservations(limit: Optional[int] = 50) -> Dict:
    """
    Lista reservas de estoque
    
    Args:
        limit: Máximo de registros
    """
    params = {"limit": min(limit or 50, 200)}
    result = await make_sienge_request("GET", "/stock-reservations", params=params)
    
    if result["success"]:
        data = result["data"]
        reservations = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontradas {len(reservations)} reservas de estoque",
            "reservations": reservations,
            "count": len(reservations)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar reservas de estoque",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ PROJETOS/OBRAS ============

@mcp.tool
async def get_sienge_projects(limit: Optional[int] = 50, offset: Optional[int] = 0, status: Optional[str] = None, search: Optional[str] = None) -> Dict:
    """
    Busca projetos/obras no Sienge
    
    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
        status: Filtrar por status
        search: Buscar por nome
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    
    if status:
        params["status"] = status
    if search:
        params["search"] = search
    
    result = await make_sienge_request("GET", "/projects", params=params)
    
    if result["success"]:
        data = result["data"]
        projects = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontrados {len(projects)} projetos",
            "projects": projects,
            "count": len(projects)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar projetos",
        "error": result.get("error"),
        "details": result.get("message")
    }

@mcp.tool
async def get_sienge_units(limit: Optional[int] = 50, offset: Optional[int] = 0) -> Dict:
    """
    Consulta unidades cadastradas no Sienge
    
    Args:
        limit: Máximo de registros (padrão: 50)
        offset: Pular registros (padrão: 0)
    """
    params = {"limit": min(limit or 50, 200), "offset": offset or 0}
    result = await make_sienge_request("GET", "/units", params=params)
    
    if result["success"]:
        data = result["data"]
        units = data.get("results", []) if isinstance(data, dict) else data
        metadata = data.get("resultSetMetadata", {}) if isinstance(data, dict) else {}
        total_count = metadata.get("count", len(units))
        
        return {
            "success": True,
            "message": f"✅ Encontradas {len(units)} unidades (total: {total_count})",
            "units": units,
            "count": len(units)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar unidades",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ CUSTOS ============

@mcp.tool
async def get_sienge_unit_cost_tables(table_code: Optional[str] = None, description: Optional[str] = None, 
                                     status: Optional[str] = "Active", integration_enabled: Optional[bool] = None) -> Dict:
    """
    Consulta tabelas de custos unitários
    
    Args:
        table_code: Código da tabela (opcional)
        description: Descrição da tabela (opcional)
        status: Status (Active/Inactive)
        integration_enabled: Se habilitada para integração
    """
    params = {"status": status or "Active"}
    
    if table_code:
        params["table_code"] = table_code
    if description:
        params["description"] = description
    if integration_enabled is not None:
        params["integration_enabled"] = integration_enabled
    
    result = await make_sienge_request("GET", "/unit-cost-tables", params=params)
    
    if result["success"]:
        data = result["data"]
        tables = data.get("results", []) if isinstance(data, dict) else data
        
        return {
            "success": True,
            "message": f"✅ Encontradas {len(tables)} tabelas de custos",
            "cost_tables": tables,
            "count": len(tables)
        }
    
    return {
        "success": False,
        "message": "❌ Erro ao buscar tabelas de custos",
        "error": result.get("error"),
        "details": result.get("message")
    }

# ============ UTILITÁRIOS ============

@mcp.tool
def add(a: int, b: int) -> int:
    """Soma dois números (função de teste)"""
    return a + b

def _get_auth_info_internal() -> Dict:
    """Função interna para verificar configuração de autenticação"""
    if SIENGE_API_KEY and SIENGE_API_KEY != "sua_api_key_aqui":
        return {
            "auth_method": "Bearer Token",
            "configured": True,
            "base_url": SIENGE_BASE_URL,
            "api_key_configured": True
        }
    elif SIENGE_USERNAME and SIENGE_PASSWORD:
        return {
            "auth_method": "Basic Auth",
            "configured": True,
            "base_url": SIENGE_BASE_URL,
            "subdomain": SIENGE_SUBDOMAIN,
            "username": SIENGE_USERNAME
        }
    else:
        return {
            "auth_method": "None",
            "configured": False,
            "message": "Configure SIENGE_API_KEY ou SIENGE_USERNAME/PASSWORD no .env"
        }

@mcp.tool
def get_auth_info() -> Dict:
    """Retorna informações sobre a configuração de autenticação"""
    return _get_auth_info_internal()

def main():
    """Entry point for the Sienge MCP Server"""
    print("* Iniciando Sienge MCP Server (FastMCP)...")
    
    # Mostrar info de configuração
    auth_info = _get_auth_info_internal()
    print(f"* Autenticacao: {auth_info['auth_method']}")
    print(f"* Configurado: {auth_info['configured']}")
    
    if not auth_info['configured']:
        print("* ERRO: Autenticacao nao configurada!")
        print("Configure as variáveis de ambiente:")
        print("- SIENGE_API_KEY (Bearer Token) OU")
        print("- SIENGE_USERNAME + SIENGE_PASSWORD + SIENGE_SUBDOMAIN (Basic Auth)")
        print("- SIENGE_BASE_URL (padrão: https://api.sienge.com.br)")
        print("")
        print("Exemplo no Windows PowerShell:")
        print('$env:SIENGE_USERNAME="seu_usuario"')
        print('$env:SIENGE_PASSWORD="sua_senha"')
        print('$env:SIENGE_SUBDOMAIN="sua_empresa"')
        print("")
        print("Exemplo no Linux/Mac:")
        print('export SIENGE_USERNAME="seu_usuario"')
        print('export SIENGE_PASSWORD="sua_senha"')
        print('export SIENGE_SUBDOMAIN="sua_empresa"')
    else:
        print("* MCP pronto para uso!")
    
    mcp.run()

if __name__ == "__main__":
    main()