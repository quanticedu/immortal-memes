import React from 'react';
import './App.css';
import gatewayUrl from './gateway';
import Modal from './modal';

const App = () => {
  return (
    <div className="container">
      <h1>Immortal Memes!</h1>
      <p>Post your best memes. But be warned: unless others rate them well, they&apos;ll be short-lived. Can you make an immortal meme?</p>
      <div className="row align-items-start">
        <div className="col-2">
          <button type="button" className="btn btn-primary">View all memes</button>
          <button type="button" className="btn btn-primary mt-3">Post a meme</button>
        </div>
        <div className="col-8 scrollable">
          
        </div>
        <div className="col-2">
          <button type="button" className="btn btn-info">Health check</button>
        </div>
      </div>
      <Modal show={!gatewayUrl}>
        <h1>Error</h1>
        <p>
          There&apos;s no gateway URL defined. Edit client/gateway.js to define it,
          then rebuild the client using &apos;npm run build&apos;.
        </p>
      </Modal>
    </div>
  );
}

export default App;
