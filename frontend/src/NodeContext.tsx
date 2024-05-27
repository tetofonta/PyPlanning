import React, {createContext, useCallback, useContext, useMemo, useState} from "react";
import {GraphEdge, GraphNode} from "reagraph";

export type Predicate = { object: string, predicate: string, params: { [k: string]: string }, value: boolean }

export type PDDLGraphData = {
    type: NodeType,
    selected?: boolean
    child?: string
    father?: string
    label: string,
    predicates: Predicate[]
}

export type PDDLGraphNode = GraphNode & PDDLGraphData

export type NodeContextType = {
    nodes: PDDLGraphNode[];
    edges: GraphEdge[];
    add_new: (father: string, child: Omit<PDDLGraphNode, "id">) => void;
    remove: (id: string) => void;
    select: (id: string) => void;
    setPredicates: (id: string, predicates: Predicate[]) => void;
    get: (id: string) => PDDLGraphData | undefined;
    changeLabel: (id: string, label: string) => void;
    reset: () => void;
}

export const NodeContext = createContext<NodeContextType>({
    nodes: [],
    edges: [],
    add_new: () => {
    },
    remove: () => {
    },
    select: () => {
    },
    setPredicates: () => {
    },
    changeLabel: () => {
    },
    get: () => undefined,
    reset: () => {
    }
})

export const useNodeContext = () => useContext(NodeContext)

export enum NodeType {
    START,
    WAYPOINT
}

const getNodeFromStep = (id: string, step: PDDLGraphData): PDDLGraphNode => {
    if (step.type === NodeType.START)
        return {
            id,
            fill: "#F00",
            ...step
        }
    else
        return {
            id,
            ...step
        }
}

const getEdges = (start: string, steps: {
    [k: string]: PDDLGraphData
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

export const NodeContextProvider = (props: { children: React.ReactElement | React.ReactElement[] }) => {

    const [steps, setSteps] = useState<{ [k: string]: PDDLGraphData }>({
        "Initial State": {type: NodeType.START, predicates: [], label: "Initial State"},
    })

    const add_new = useCallback((father: string, child: Omit<PDDLGraphNode, "id">) => {
        if (!steps[father]) return;
        const id = Math.random().toString(26).substring(2)
        setSteps(s => ({
            ...s,
            [father]: {...s[father], child: id},
            [id]: {...child, father, child: s[father].child}
        }));
    }, [steps])

    const remove = useCallback((id: string) => {
        if (!steps[id]) return;
        const new_steps = {...steps}
        const old_child = steps[id].child
        const old_father = steps[id].father
        if (!old_father) return;
        new_steps[old_father].child = old_child
        delete new_steps[id]
        setSteps(new_steps)
    }, [steps])

    const setPredicates = useCallback((id: string, predicates: Predicate[]) => setSteps(e => ({
        ...e,
        [id]: {...e[id], predicates}
    })), [steps])
    const get = useCallback((id: string) => steps[id], [steps])

    const changeLabel = useCallback((id: string, label: string) => {
        setSteps(s => ({...s, [id]: {...s[id], label}}))
    }, [steps])

    const nodes = useMemo(() => Object.keys(steps).map(k => getNodeFromStep(k, steps[k])), [steps])
    const edges = useMemo(() => getEdges("Initial State", steps), [steps])

    console.log(steps)

    return <NodeContext.Provider value={{
        nodes,
        edges,
        add_new,
        remove,
        setPredicates,
        get,
        changeLabel: changeLabel,
        reset: () => setSteps({
            "Initial State": {type: NodeType.START, predicates: [], label: "Initial State"},
        }),
        select: () => {
        }
    }}>
        {props.children}
    </NodeContext.Provider>

}