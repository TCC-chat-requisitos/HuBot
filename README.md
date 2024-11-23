# **HUBOT**

### **Como Configurar e Rodar o Chatbot (Sistemas Debian/Ubuntu)**

1. **Certifique-se de que os pacotes essenciais estão instalados**:  
   Antes de configurar o chatbot, instale as dependências básicas do sistema.  
   ```bash
   sudo apt update && sudo apt upgrade
   sudo apt install -y python3 python3-venv python3-pip
   ```

2. **Clone o repositório**:  
   Faça o download do código-fonte do chatbot.  
   ```bash
   git clone https://github.com/seu-usuario/hubot.git
   cd Hubot
   ```

3. **Crie um ambiente virtual (venv)**:  
   Um ambiente virtual ajuda a isolar as dependências do projeto.  
   ```bash
   python3 -m venv venv
   ```

4. **Ative o ambiente virtual**:  
   ```bash
   source venv/bin/activate
   ```

5. **Instale as dependências do projeto**:  
   Com o ambiente virtual ativado, instale as bibliotecas necessárias.  
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

6. **Inicie os serviços do RASA**:  
   Com as dependências instaladas, inicie o chatbot:  
   - Entre na pasta 'hubot':  
     ```bash
     cd hubot/
     ```  
   - Execute o servidor de ações:  
     ```bash
     rasa run actions
     ```  
   - Em outro terminal (com o venv ativado), execute o servidor principal:  
     ```bash
     rasa run
     ```  

     OU
     
   - Caso queira interagir com o HuBot diretamente no terminal:
    ```bash
    rasa shell
    ```

7. **Interaja com o chatbot**:  
   Após os passos anteriores, o chatbot estará disponível localmente no endereço:  
   ```
   http://localhost:5005
   ```  
   Use um cliente HTTP como o **Postman**, o **Insomnia**, integre com seu frontend ou utilize o próprio terminal (Caso tenha optado pelo 'rasa shell').
---

### **Nota Importante**  
Este projeto **não** possui controle sobre as respostas geradas pela API da OpenAI. Os desenvolvedores não assumem responsabilidade pelo conteúdo gerado. Consulte os [termos de uso da OpenAI](https://openai.com/terms/) para mais informações.  

---

### Licença

Este projeto está licenciado sob os termos da [Licença MIT](./LICENSE).