import { useState } from 'react';
import './App.css'
import styles from "./App.module.css";
import Message from './component/message/Message';
import MessageInput from './component/MessageInput/MessageInput';
import Modal from './component/Modal/Modal';


function App() {
  const [showModal, setShowModal] = useState(false);
  const [selectId, setSelectId] = useState();
  const [message, setMessage] = useState([
    {
      id: 1,
      text: "message1",
      createdAt: new Date(),
    },
    {
      id: 2,
      text: "message2",
      createdAt: new Date(),
    },
  ]);
  

  return <main className={styles.container}>
    <section className={styles.chattingSection}>
      <div className={styles.messageSection}>
        {message.map((message) => {
          return <Message 
            key={message.id}
            id={message.id}
            text={message.text}
            setSelectId={setSelectId}
            setShowModal={setShowModal}
          />;
        })}
      </div>
      <MessageInput setMessage={setMessage}/>
    </section>
    {showModal && <Modal
      selectId={selectId}
      setMessage={setMessage}
      setShowModal={setShowModal}
    />}
  </main>;
}

export default App;