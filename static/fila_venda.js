function atualizarNumerosOrdem(container) {
    container.querySelectorAll('.kanban-card').forEach((card, idx) => {
        const ordemSpan = card.querySelector('.ordem');
        if (ordemSpan) ordemSpan.textContent = `#${idx + 1}`;
    });
}

document.addEventListener('DOMContentLoaded', function () {
    // Inicializar Sortable em cada coluna
    document.querySelectorAll('.kanban-items-container').forEach(function (container) {
        new Sortable(container, {
            animation: 150,
            handle: '.kanban-card',
            filter: '.btn-remover-vendedor',
            onEnd: function () {
                const grupo = container.closest('.kanban-column').querySelector('input[name="grupo"]').value;
                const ids = Array.from(container.querySelectorAll('.kanban-card')).map(card => card.dataset.id);
                fetch('/api/fila_venda/ordenar', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ grupo: grupo, ordem: ids })
                });
                atualizarNumerosOrdem(container);
            }
        });
    });

    document.querySelectorAll('.form-add-vendedor').forEach(form => {
        form.addEventListener('submit', async function (e) {
            e.preventDefault();
            const nome = this.querySelector('input[name="nome"]').value.trim();
            const grupo = this.querySelector('input[name="grupo"]').value;
            if (!nome) return alert('Digite o nome do vendedor!');
            const resp = await fetch('/api/fila_venda', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ nome, grupo })
            });
            if (resp.ok) location.reload();
            else alert('Erro ao adicionar vendedor');
        });
    });

    document.querySelectorAll('.btn-remover-vendedor').forEach(btn => {
        btn.addEventListener('click', async function () {
            if (!confirm('Remover este vendedor?')) return;
            const id = this.dataset.id;
            const resp = await fetch('/api/fila_venda/' + id, { method: 'DELETE' });
            if (resp.ok) location.reload();
            else alert('Erro ao remover vendedor');
        });
    });


});
