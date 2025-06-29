#!/usr/bin/env python3
"""
Script para consultar o banco de dados do EditalBot
Usage: python consulta_banco.py
"""

import sqlite3
from database import db
from datetime import datetime

def consulta_usuarios():
    """Consulta todos os usuários"""
    print("=== USUÁRIOS ===")
    users = db.get_all_users()
    for user in users:
        print(f"ID: {user['id']}")
        print(f"Nome: {user['name']}")
        print(f"Email: {user['email']}")
        print(f"Domínio: {user['domain']}")
        print(f"Primeiro login: {user['first_login']}")
        print(f"Último acesso: {user['last_access']}")
        print(f"Quantidade de acessos: {user['access_count']}")
        print("-" * 50)

def consulta_mensagens(user_id=None):
    """Consulta mensagens (de um usuário específico ou todas)"""
    print("=== MENSAGENS ===")
    
    if user_id:
        messages = db.get_user_messages(user_id)
        print(f"Mensagens do usuário ID {user_id}:")
    else:
        # Consulta todas as mensagens via SQL direto
        conn = sqlite3.connect('editalbot.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.*, u.name, u.email 
            FROM messages m 
            JOIN users u ON m.user_id = u.id 
            ORDER BY m.timestamp DESC
        """)
        messages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        print("Todas as mensagens:")
    
    for msg in messages:
        print(f"ID: {msg['id']}")
        if 'name' in msg:
            print(f"Usuário: {msg['name']} ({msg['email']})")
        print(f"Mensagem: {msg['user_message']}")
        print(f"Resposta: {msg['bot_response']}")
        print(f"Contexto: {msg['notice_context']}")
        print(f"Timestamp: {msg['timestamp']}")
        print("-" * 50)

def estatisticas():
    """Mostra estatísticas gerais"""
    print("=== ESTATÍSTICAS ===")
    stats = db.get_user_stats()
    
    print(f"Total de usuários: {stats['total_users']}")
    print(f"Usuários recentes (7 dias): {stats['recent_users']}")
    print(f"Total de mensagens: {stats['total_messages']}")
    
    print("\nDistribuição por domínio:")
    for domain, count in stats['domain_stats'].items():
        print(f"  {domain}: {count} usuários")
    
    # Estatísticas de uso de editais
    notice_usage = db.get_notice_usage()
    if notice_usage:
        print("\nUso de editais:")
        for usage in notice_usage:
            print(f"  {usage['notice_context']}: {usage['usage_count']} consultas")

def consulta_sql_personalizada():
    """Permite executar consultas SQL personalizadas"""
    print("=== CONSULTA SQL PERSONALIZADA ===")
    print("Digite uma consulta SQL (ou 'exit' para sair):")
    
    conn = sqlite3.connect('editalbot.db')
    conn.row_factory = sqlite3.Row
    
    while True:
        query = input("SQL> ").strip()
        if query.lower() == 'exit':
            break
        
        try:
            cursor = conn.cursor()
            cursor.execute(query)
            
            if query.lower().startswith('select'):
                results = cursor.fetchall()
                if results:
                    # Mostrar cabeçalhos
                    print("| " + " | ".join(results[0].keys()) + " |")
                    print("|-" + "-|-".join(["-" * len(key) for key in results[0].keys()]) + "-|")
                    
                    # Mostrar dados
                    for row in results:
                        print("| " + " | ".join([str(value) for value in row]) + " |")
                else:
                    print("Nenhum resultado encontrado.")
            else:
                conn.commit()
                print(f"Query executada. Linhas afetadas: {cursor.rowcount}")
        
        except Exception as e:
            print(f"Erro: {e}")
    
    conn.close()

def main():
    """Função principal"""
    while True:
        print("\n" + "="*60)
        print("CONSULTA DO BANCO DE DADOS - EDITALBOT")
        print("="*60)
        print("1. Consultar usuários")
        print("2. Consultar todas as mensagens")
        print("3. Consultar mensagens de um usuário específico")
        print("4. Estatísticas gerais")
        print("5. Consulta SQL personalizada")
        print("0. Sair")
        
        escolha = input("\nEscolha uma opção: ").strip()
        
        if escolha == "1":
            consulta_usuarios()
        elif escolha == "2":
            consulta_mensagens()
        elif escolha == "3":
            user_id = input("Digite o ID do usuário: ").strip()
            try:
                consulta_mensagens(int(user_id))
            except ValueError:
                print("ID inválido!")
        elif escolha == "4":
            estatisticas()
        elif escolha == "5":
            consulta_sql_personalizada()
        elif escolha == "0":
            break
        else:
            print("Opção inválida!")
        
        input("\nPressione Enter para continuar...")

if __name__ == "__main__":
    main()
