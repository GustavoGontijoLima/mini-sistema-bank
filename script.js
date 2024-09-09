document.getElementById('loginForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const cpf = document.getElementById('cpf').value;
    const senha = document.getElementById('senha').value;

    fetch('/login', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `cpf=${cpf}&senha=${senha}`
    }).then(response => response.text()).then(data => {
        alert(data);
        if (data === "Login bem-sucedido" && cpf === 'admin' && senha === 'admin') {
            window.location.href = '/visualizar_banco.html';
        }
        else if (data === "Login bem-sucedido"){
            window.location.href = '/dashboard.html';
        }
    });
});

document.getElementById('cadastroForm')?.addEventListener('submit', function(event) {
    event.preventDefault();
    const nome = document.getElementById('nome').value;
    const cpf = document.getElementById('cpf').value;
    const data_nascimento = document.getElementById('data_nascimento').value;
    const senha = document.getElementById('senha').value;

    fetch('/cadastrar', {
        method: 'POST',
        headers: {'Content-Type': 'application/x-www-form-urlencoded'},
        body: `nome=${nome}&cpf=${cpf}&data_nascimento=${data_nascimento}&senha=${senha}`
    }).then(response => response.text()).then(data => {
        alert(data);
        if (data === "Usuario cadastrado com sucesso!") {
            window.location.href = '/login.html';
        }
    });
});
