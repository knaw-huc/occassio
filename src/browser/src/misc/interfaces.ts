// import * as queryString from "querystring";

export interface IFacetCandidate {
    facet: string,
    field: string,
    candidate: string
}

export interface ISendCandidate {
    (data: IFacetCandidate):void
}

enum FacetType {
    Text = "text",
    Number = "number",
}

export interface IFacet {
    field: string,
    type: FacetType
    name: string,
}

export interface INumberFacet extends IFacet {
    type: FacetType.Number
    min: number,
    max: number
}

export interface IResultItem {
    id: string,
    message_id: string,
    subject: string,
    from_name: string,
    from_email: string,
    date: string,
    lines: string,
    newsgroups: string[],
    path: string,
    x_gateway: string,
    xref: string,
}

export interface IDetail {
    id: string,
    subject: string,
    body: string,
    path: string,
    from_name: string,
    from_email: string,
    newsgroups: string[],
    message_id: string,
    date: string,
    x_gateway: string,
    lines: number,
    xref: string,
    thread_reply?: IResultItem|null
    replies?: IDetail[]
}


