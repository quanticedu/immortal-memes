import React, { useState } from 'react';
import Modal from './modal';

const TextInputModal = ({ show, onOk, onCancel, children }) => {
    const [ inputValue, setInputValue ] = useState("");

    const onTextChanged = (event) => {
        setInputValue(event.target.value);
    }

    return (
        <Modal show={show}>
            {children}
            <div className="container">
                <div className="row justify-content-center">
                    <div className="input-group col-3">
                        <input className="form-control" type="text" onChange={onTextChanged} />
                        <button className="btn btn-primary ms-2" onClick={() => onOk(inputValue)}>Ok</button>
                        <button className="btn btn-secondary ms-2" onClick={onCancel}>Cancel</button>
                    </div>
                </div>
            </div>
        </Modal>
    );
}

export default TextInputModal;