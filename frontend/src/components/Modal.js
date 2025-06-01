import React from 'react';
import './Modal.css'; 

const Modal = ({ isOpen, onClose, title, children }) => {
  if (!isOpen) {
    return null;
  }

  return (
    <>
      <div className="modal-overlay" onClick={onClose} />
      <div className="modal-container">
        <div className="modal-header">
          {title && <h3 className="modal-title">{title}</h3>}
          <button onClick={onClose} className="modal-close-button">×</button>
        </div>
        <div className="modal-body">
          {children}
        </div>
      </div>
    </>
  );
};

export default Modal;