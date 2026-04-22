prompt_sumarizado = """
        Você é um arquivista técnico. Resuma a conversa abaixo em tópicos objetivos.
        resuma seguindo a sequencia de topicos abaixo : 

        - Assunto da conversa 
        - Decisões tomadas pelo usuário 
        - interesses demonstrados na conversa
        - pretenções do usuário 

        ( e aqui preencha com um resumo previo da conversa, resumindo os topicos acima, e a conversa em um paragráfo)

        Conversa: {historico}
        """