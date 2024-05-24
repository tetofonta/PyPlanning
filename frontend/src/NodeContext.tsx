import {createContext, useCallback, useContext, useEffect, useState} from "react";
import {GraphEdge, GraphNode} from "reagraph";

export type NodeContextType = {
    nodes: GraphNode[];
    edges: GraphEdge[];
    add_new: (father: string, child: { node: NodeType, id: string }) => void;
    remove: (id: string) => void;
    select: (id: string) => void;
}

export const NodeContext = createContext<NodeContextType>({
    nodes: [],
    edges: [],
    add_new: () => {
    },
    remove: () => {
    },
    select: () => {
    }
})

export const useNodeContext = () => useContext(NodeContext)

export enum NodeType {
    START,
    WAYPOINT
}

const getNodeFromStep = (id: string, step: { node: NodeType, father?: string | null, child?: string | null }) => {
    if (step.node === NodeType.START)
        return {
            id,
            fill: "#F00",
            label: "Current State",
            node: step.node
        }
    else
        return {
            id,
            label: id,
            node: step.node
        }
}

const getEdges = (start: string, steps: {
    [k: string]: { node: NodeType, father?: string | null, child?: string | null }
}): GraphEdge[] => {
    const ret: GraphEdge[] = []
    let a_k: string | null | undefined = start
    let b_k: string | null | undefined = steps[start].child
    while (b_k != null && a_k != null) {
        ret.push({
            id: `${a_k}->${b_k}`,
            source: a_k,
            target: b_k
        })
        a_k = b_k
        b_k = b_k ? steps[b_k].child : null
    }
    return ret
}

const steps: {
    [k: string]: { node: NodeType, father?: string | null, child?: string | null }
} = {"START": {node: NodeType.START, father: null, child: null}}


export const NodeContextProvider = (props: { children: any }) => {

    const [state, setState] = useState<NodeContextType>(
        {
            nodes: [],
            edges: [],
            add_new: () => {
            },
            remove: () => {
            },
            select: () => {
            }
        })

    const add_new = useCallback((father: string, child: { node: NodeType, id: string }) => {
        console.log("AAAA")
        if (!steps[father]) return;
        steps[father] = {...steps[father], child: child.id};
        steps[child.id] = {node: child.node, father, child: null}
        setState(state => ({
            ...state,
            edges: getEdges("START", steps),
            nodes: Object.keys(steps).map(k => getNodeFromStep(k, steps[k]))
        }))
    }, [])

    useEffect(() => {
        setState(state => ({
            ...state,
            edges: [],
            nodes: Object.keys(steps).map(k => getNodeFromStep(k, steps[k])),
            add_new
        }))
    }, [add_new])

    return <NodeContext.Provider value={state}>
        {props.children}
    </NodeContext.Provider>

}