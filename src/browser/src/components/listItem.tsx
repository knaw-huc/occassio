import {Link} from 'react-router-dom';
import {IResultItem} from '../misc/interfaces';

export default function ListItem({item}: {item: IResultItem}) {
    const date = new Date(item.date);

    return (
        <div className={'hcResultListDetail'}>
            <h2><Link to={'/detail/' + encodeURI(item.id)}>{item.subject}</Link></h2>
            <small>{item.from_email}, {item.newsgroups}</small><br />
            <small>{date.toLocaleString()}</small>
        </div>
    );
}
