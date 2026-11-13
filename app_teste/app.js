
const form = document.querySelector('form');
const feedback = document.querySelector('#feedback');

form.addEventListener('submit', async event => {
  event.preventDefault();
  const button = form.querySelector('button');
  const admin = form.id === 'admin';
  const data = Object.fromEntries(new FormData(form));

  button.disabled = true;
  feedback.textContent = admin ? 'Consultando…' : 'Enviando…';

  if (admin) document.querySelector('#messages').replaceChildren();

  try {
    const options = admin
      ? {headers: {
          Authorization: 'Basic ' + btoa(
            String.fromCharCode(...new TextEncoder().encode('admin:' + data.password))
          )
        }}
      : {
          method: 'POST',
          headers: {'Content-Type': 'application/json'},
          body: JSON.stringify(data)
        };

    const response = await fetch('/api/messages', options);
    const result = await response.json();

    if (!response.ok) throw new Error(result.error || 'Não foi possível concluir.');

    if (admin) {
      feedback.textContent = result.messages.length + ' mensagem(ns) encontrada(s).';

      for (const message of result.messages) {
        const article = document.createElement('article');

        for (const [tag, text] of [
          ['h3', message.name],
          ['p', message.email],
          ['small', new Date(message.created_at).toLocaleString('pt-BR')],
          ['p', message.message]
        ]) {
          const element = document.createElement(tag);
          element.textContent = text;
          article.append(element);
        }

        document.querySelector('#messages').append(article);
      }
    } else {
      feedback.textContent = result.message + ' Protocolo #' + result.id + '.';
    }

    form.reset();
  } catch (error) {
    feedback.textContent = error.message;
  } finally {
    button.disabled = false;
  }
});
