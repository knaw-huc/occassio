import {IDetail} from "../misc/interfaces.ts";
import {NewsgroupLabel} from "./newsgroupLabel.tsx";

export function DetailContents({data}: {data: IDetail}) {
    const date = new Date(data.date);

    function renderNewsgroups() {
        let newsgroups: string[];
        if (typeof data.newsgroups === "string") {
            newsgroups = [data.newsgroups];
        } else {
            newsgroups = data.newsgroups;
        }
        return newsgroups.map(label => {
            return <NewsgroupLabel key={label} newsGroup={label} />
        });
    }

    return (
        <>
            <h2>{data.subject}</h2>
            <small>
                Written by {data.from_name} ({data.from_email})<br/>
                {renderNewsgroups()}<br/>
                {date.toLocaleString()}
            </small>
            <pre>
                {data.body}
            </pre>
        </>
    )
}
