// Función para abrir el modal de añadir cliente
function openAddClientModal() {
    const addClientModal = document.getElementById("addClientModal");
    const addClientSelect = document.getElementById("addClientSelect");
    
    // Limpiar opciones previas
    addClientSelect.innerHTML = '';

    // Añadir todos los clientes a la lista de selección, excepto los ya presentes en el reparto
    const currentClients = document.getElementById("clientes").options;
    const clientesDisponibles = JSON.parse(document.getElementById("clientesData").textContent);

    clientesDisponibles.forEach(client => {
        let isInCurrentList = false;
        for (let i = 0; i < currentClients.length; i++) {
            if (currentClients[i].value === client.id) {
                isInCurrentList = true;
                break;
            }
        }
        if (!isInCurrentList) {
            const option = document.createElement("option");
            option.value = client.id;
            option.text = client.username;
            addClientSelect.appendChild(option);
        }
    });

    // Mostrar el modal
    addClientModal.style.display = "block";
}

// Función para añadir un cliente al reparto
function addClient() {
    const addClientSelect = document.getElementById("addClientSelect");
    const selectedClientId = addClientSelect.value;
    const selectedClientText = addClientSelect.options[addClientSelect.selectedIndex].text;

    // Verificar que se haya seleccionado un cliente
    if (!selectedClientId) {
        alert("Por favor selecciona un cliente para añadir.");
        return;
    }

    // Añadir cliente a la lista de clientes del reparto
    const clientesSelect = document.getElementById("clientes");
    const newOption = document.createElement("option");
    newOption.value = selectedClientId;
    newOption.text = selectedClientText;
    clientesSelect.appendChild(newOption);

    // Cerrar el modal
    document.getElementById("addClientModal").style.display = "none";
}

// Función para eliminar el cliente seleccionado
function removeSelectedClient() {
    const clientesSelect = document.getElementById("clientes");
    const selectedIndex = clientesSelect.selectedIndex;

    if (selectedIndex === -1) {
        alert("Por favor selecciona un cliente para eliminar.");
        return;
    }

    // Eliminar cliente seleccionado
    clientesSelect.remove(selectedIndex);
}

// Función para cambiar el cliente seleccionado
function changeSelectedClient() {
    const clientesSelect = document.getElementById("clientes");
    const selectedIndex = clientesSelect.selectedIndex;

    if (selectedIndex === -1) {
        alert("Por favor selecciona un cliente para cambiar.");
        return;
    }

    const selectedClientId = clientesSelect.options[selectedIndex].value;
    const selectedClientText = clientesSelect.options[selectedIndex].text;

    // Abrir el modal de selección de nuevo cliente
    const addClientModal = document.getElementById("addClientModal");
    const addClientSelect = document.getElementById("addClientSelect");
    addClientSelect.innerHTML = '';

    // Añadir todos los clientes disponibles excepto el cliente actual que se desea cambiar
    const clientesDisponibles = JSON.parse(document.getElementById("clientesData").textContent);

    clientesDisponibles.forEach(client => {
        if (client.id !== selectedClientId) {
            const option = document.createElement("option");
            option.value = client.id;
            option.text = client.username;
            addClientSelect.appendChild(option);
        }
    });

    // Guardar el índice seleccionado y abrir el modal
    addClientModal.dataset.changeIndex = selectedIndex;
    addClientModal.dataset.isChange = "true";
    addClientModal.style.display = "block";
}

// Modificar la función addClient para admitir el cambio de cliente también
document.getElementById("addClientModal").addEventListener("click", function(event) {
    if (event.target.matches(".btn-primary")) {
        const addClientSelect = document.getElementById("addClientSelect");
        const selectedClientId = addClientSelect.value;
        const selectedClientText = addClientSelect.options[addClientSelect.selectedIndex].text;

        if (!selectedClientId) {
            alert("Por favor selecciona un cliente para añadir o cambiar.");
            return;
        }

        const addClientModal = document.getElementById("addClientModal");
        const isChange = addClientModal.dataset.isChange === "true";

        if (isChange) {
            // Cambio de cliente
            const changeIndex = addClientModal.dataset.changeIndex;
            const clientesSelect = document.getElementById("clientes");

            // Reemplazar cliente en la lista
            clientesSelect.options[changeIndex].value = selectedClientId;
            clientesSelect.options[changeIndex].text = selectedClientText;

            addClientModal.dataset.isChange = "false"; // Resetear para próximas acciones
        } else {
            // Añadir cliente nuevo
            addClient();
        }

        // Cerrar el modal
        addClientModal.style.display = "none";
    }
});
