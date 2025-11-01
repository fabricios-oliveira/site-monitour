// Usa o inicializador de jQuery do admin do Django, que garante que o jQuery já foi carregado.
(function($) {
    // Usamos o seletor de ID que o Django admin gera para os campos
    const cpfInput = document.getElementById('id_cpf');
    const telefoneInput = document.getElementById('id_telefone');

    if (cpfInput) {
        // Aplica a máscara de CPF
        // O plugin de máscara precisa ser carregado no base_site.html para estar disponível aqui.
        $(cpfInput).mask('000.000.000-00', {reverse: true});

        // Adiciona o botão de verificação de CPF
        const cpfHelp = cpfInput.closest('.form-row').querySelector('.help');
        if (cpfHelp) {
            cpfHelp.innerHTML += `
                <button type="button" id="verify-cpf-btn" class="button" style="margin-left: 10px;">Verificar CPF</button>
                <span id="cpf-status" style="margin-left: 10px; font-weight: bold;"></span>
            `;
        }

        document.getElementById('verify-cpf-btn').addEventListener('click', function() {
            const cpf = cpfInput.value;
            const statusSpan = document.getElementById('cpf-status');
            
            if (!cpf || cpf.length < 14) {
                statusSpan.textContent = 'CPF inválido.';
                statusSpan.style.color = 'orange';
                return;
            }

            // Pega o ID do cliente da URL (se estiver na página de edição)
            const pathParts = window.location.pathname.split('/');
            const clienteId = pathParts[pathParts.length - 3]; // /admin/app/model/ID/change/

            // Monta a URL da nossa nova view de verificação
            const url = `/cadastros/verificar-cpf/?cpf=${encodeURIComponent(cpf)}&cliente_id=${clienteId || ''}`;

            statusSpan.textContent = 'Verificando...';
            statusSpan.style.color = 'black';

            fetch(url)
                .then(response => response.json())
                .then(data => {
                    if (data.exists) {
                        statusSpan.textContent = 'CPF já cadastrado!';
                        statusSpan.style.color = 'red';
                    } else {
                        statusSpan.textContent = 'CPF disponível!';
                        statusSpan.style.color = 'green';
                    }
                })
                .catch(error => {
                    statusSpan.textContent = 'Erro na verificação.';
                    statusSpan.style.color = 'red';
                    console.error('Error:', error);
                });
        });
    }

    if (telefoneInput) {
        // Aplica a máscara de telefone
        var SPMaskBehavior = function (val) {
          return val.replace(/\D/g, '').length === 11 ? '(00) 00000-0000' : '(00) 0000-00009';
        },
        spOptions = { onKeyPress: function(val, e, field, options) { field.mask(SPMaskBehavior.apply({}, arguments), options); } };
        $(telefoneInput).mask(SPMaskBehavior, spOptions);
    }
})(django.jQuery);