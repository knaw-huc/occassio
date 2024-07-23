import {useNavigate} from "react-router-dom";

export function NewsgroupLabel({newsGroup}: {newsGroup: string}) {

    const navigate = useNavigate();

    function goToNewsgroup() {
        navigate("/search?newsgroups=" + encodeURIComponent(newsGroup));
    }

    return <span className={'label'} onClick={goToNewsgroup}>{newsGroup}</span>
}
