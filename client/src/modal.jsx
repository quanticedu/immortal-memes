// modal courtesy of Dave Ceddia, https://daveceddia.com/open-modal-in-react/
import './App.css';

const Modal = ({ show, children }) => {
    return show ? (
        <div className="modalBackdrop">
            <div className="modalBox">
                {children}
            </div>
        </div>
    ) : null;
}

export default Modal;