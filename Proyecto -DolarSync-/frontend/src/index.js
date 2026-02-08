import React, { useEffect, useState } from 'react';

function App() {
  const [dolar, setDolar] = useState(null);

  useEffect(() => {
    fetch('/api/dolar-bcv')
      .then(res => res.json())
      .then(data => setDolar(data.dolar_bcv));
  }, []);

  return (
    <div>
      <h1>Valor del Dólar BCV</h1>
      {dolar ? <p>{dolar}</p> : <p>Cargando...</p>}
    </div>
  );
}

export default App;