import styles from "./MessageInput.module.css"
import { useState } from "react";

function MessageInput({setMessage}){

    const [inputValue, setInputValue] = useState("");

    return (
        <div className={styles.container}>
            <input 
            value={inputValue}
                onChange={(e) => {
                    setInputValue(e.target.value);
                }}
            />
            <button onClick={() => {
                setMessage((prev) => {
                    return [
                        ...prev, 
                        {
                        id: prev.length + 1,
                        text: inputValue,
                        createAt: new Date(),
                        },
                    ]
                });
                setInputValue("");
            }}>전송</button>
        </div>
    )
}
export default MessageInput