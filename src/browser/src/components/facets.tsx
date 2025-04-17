import {FreeTextFacet, ListFacet, SliderFacet} from '@knaw-huc/browser-base-react';
import {FACET_URL, getApiBase} from "../misc/config";
import {useEffect, useState} from "react";
import {IFacet, INumberFacet} from "../misc/interfaces.ts";
import {useAuth} from "react-oidc-context";
import {FacetsRequestParams} from "@knaw-huc/browser-base-react/dist/cjs/types/hooks/useListFacet";

export default function Facets() {

    const [facets, setFacets] = useState([] as IFacet[]);
    const  auth = useAuth();
    const token = auth.user?.access_token

    useEffect(() => {
        if (!token) {
            return;
        }
        fetch(getApiBase() + '/api/facets', {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }).then((response) => {
            response.json().then(data => {
                setFacets(data);
            });
        })
    }, []);

    /*
    const doPost = async () => fetch(url, {
        method: 'POST',
        headers: {
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            name: field,
            amount: amount,
            filter: filter,
            searchvalues: searchValues
        })
    });
     */

    const objects = facets.map((facet ) => {
        switch (facet.type) {
            case "text": {
                return <ListFacet
                    key={facet.field}
                    name={facet.name}
                    field={facet.field}
                    url={getApiBase() + FACET_URL}
                    flex={false}
                    usePost={true}
                    facetsRequest={async (params: FacetsRequestParams) => {
                        let response = await fetch(getApiBase() + FACET_URL, {
                            method: "POST",
                            headers: {
                                "Accept": "application/json",
                                "Content-Type": "application/json",
                                "Authorization": `Bearer ${token}`
                            },
                            body: JSON.stringify(params)
                        })
                        return response.json()
                    }}
                    addFilter={true} />
            }
            case "number": {
                const numFacet = facet as INumberFacet
                return <SliderFacet
                    key={numFacet.field}
                    name={numFacet.name}
                    field={numFacet.field}
                    min={numFacet.min}
                    max={numFacet.max} />
            }
        }
    })

    return <>
        <FreeTextFacet />
        {objects}
    </>;
}
