import styles from "./Modal.module.css";

function Modal ({selectId, setMessage, setShowModal}) {
    const handleConfirmClick = () => {
        setMessage((prev) => {
            return prev.filter((message) => message.id !== selectId);
        });
        setShowModal(false);
    };
    const handleCancelClick = () => {
        setShowModal(false);
    };

    return (
        <section className={styles.container}>
            <span>정말 삭제 하시겠습니까?</span>
            <div className={styles.buttonSection}>
                <button onClick={handleConfirmClick}>확인</button>
                <button onClick={handleCancelClick}>취소</button>
            </div>
        </section>
    );
}

export default Modal;