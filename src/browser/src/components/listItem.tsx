import {Link} from 'react-router-dom';
import {IResultItem} from '../misc/interfaces';

export default function ListItem({item}: {item: unknown}) {
    const it: IResultItem = item as IResultItem
    const date = new Date(it.date);

    return (
        <div className={'hcResultListDetail'}>
            <h2><Link to={'/detail/' + encodeURI(it.id)}>{it.subject}</Link></h2>
            <small>{it.from_email}, {it.newsgroups}</small><br />
            <small>{date.toLocaleString()}</small>
        </div>
    );
}
