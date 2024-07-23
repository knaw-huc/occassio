import {IDetail, IResultItem} from "../misc/interfaces";
import {useState} from "react";
import {DetailContents} from "./detailContents.tsx";
import {useNavigate} from "react-router-dom";

export function Detail({data}: {data: IDetail}) {
    const [selectedItem, setSelectedItem] = useState<string>(data.id);

    const date = new Date(data.date);

    const navigate = useNavigate();

    function getData(id: string): IDetail {
        if (data.replies === undefined || data.replies.length === 0) {
            return data;
        }
        const allOptions = [
            data,
            ... data.replies as IDetail[]
        ];
        for (const option of allOptions) {
            if (option.id === id) {
                return option;
            }
        }
        return data;
    }

    function getName(data: IDetail): string {
        if (data.from_name == 'No name given') {
            return data.from_email;
        }
        return data.from_name;
    }

    function renderOriginalPost() {
        if (!('thread_reply' in data)) {
            return;
        }
        if (data.thread_reply == null) {
            return <>
                <h2>Original post:</h2>
                <p>Not available in dataset</p>
            </>
        }
        const original = data.thread_reply as IResultItem
        const originalDate = new Date(data.date);
        return <>
            <div className={"thread-navigator"}>
                <header>
                    <h2>Part of thread:</h2>
                </header>
                <ul>
                    <li className={'thread-navigator-button'} onClick={() => {navigate('/detail/' + original.id)}}>
                        <h4>{original.subject}</h4>
                        <small>{originalDate.toLocaleString()}</small>
                    </li>
                </ul>
            </div>
        </>
    }

    function renderReplies() {
        if (!('replies' in data)) {
            return;
        }
        const repliesJsx = (data.replies as IDetail[]).map(reply => {
            const replyDate = new Date(reply.date);
            return <li key={reply.id} onClick={() => {setSelectedItem(reply.id)}} className={"thread-navigator-button" + (selectedItem == reply.id ? " active" : "")}>
                <h4>{getName(reply)}</h4>
                <small>{replyDate.toLocaleString()}</small>
            </li>
        })

        return <>
            <div className={"thread-navigator"}>
                <header>
                    <h2>Thread:</h2>
                </header>
                <ul>
                    <li onClick={() => {setSelectedItem(data.id)}} className={"thread-navigator-button" + (selectedItem == data.id ? " active" : "")}>
                        <h4>Original post</h4>
                        <small>{date.toLocaleString()}</small>
                    </li>
                    {repliesJsx}
                </ul>
            </div>
        </>
    }

    return (
        <>
            <div className={"row"}>
                <div className={"main-content"}>
                    <div className={"justify hcMarginBottom1"}>
                        <DetailContents data={getData(selectedItem)} />
                    </div>
                </div>
                <div className={'side-bar'}>
                    {renderOriginalPost()}
                    {renderReplies()}
                </div>
            </div>
        </>
    )
}
