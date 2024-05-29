import React, {createContext, useCallback, useContext, useMemo, useState} from "react";
import {GraphEdge, GraphNode} from "reagraph";

export type Predicate = { object: string, predicate: string, params: { [k: string]: string }, value: boolean }

export type PDDLGraphData = {
    type: NodeType;
    selected?: boolean;
    child?: string;
    father?: string;
    label: string;
    predicates: Predicate[];
}

export type PDDLGraphNode = GraphNode & PDDLGraphData

export type NodeContextType = {
    nodes: PDDLGraphNode[];
    edges: GraphEdge[];
    add_new: (father: string, child: Omit<PDDLGraphNode, "id">) => void;
    append_new: (child: Omit<PDDLGraphNode, "id">) => void;
    remove: (id: string) => void;
    select: (id: string) => void;
    next: () => void;
    hasNext: () => boolean;
    setPredicates: (id: string, predicates: Predicate[]) => void;
    get: (id: string) => PDDLGraphData | undefined;
    getSelected: () => PDDLGraphData | undefined;
    getNextWaypoint: () => PDDLGraphData | undefined;
    changeLabel: (id: string, label: string) => void;
    reset: () => void;
}

export const NodeContext = createContext<NodeContextType>({
    nodes: [],
    edges: [],
    add_new: () => {
    },
    append_new: () => {
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
    },
    next: () => {
    },
    getSelected: () => undefined,
    getNextWaypoint: () => undefined,
    hasNext: () => false
})

export const useNodeContext = () => useContext(NodeContext)

export enum NodeType {
    START,
    WAYPOINT,
    ACTION
}

const getNodeFromStep = (id: string, step: PDDLGraphData): PDDLGraphNode => {
    switch (step.type){
        case NodeType.START:
            return {
                id,
                fill: "#F00",
                ...step,
                label: step.selected ? `[${step.label || id}]`: (step.label || id)
            }
        case NodeType.WAYPOINT:
            return {
                id,
                fill: "#123",
                ...step,
                label: step.selected ? `[${step.label || id}]`: (step.label || id)
            }
        case NodeType.ACTION:
            return {
                id,
                fill: "#3e7cb6",
                ...step,
                label: step.selected ? `[${step.label || id}]`: (step.label || id),
                size: 6
            }
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
        "Initial State": {type: NodeType.START, predicates: [], label: "Initial State", selected: true},
    })
    const [selected, setSelected] = useState<string>("Initial State")

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
    const getSelected = useCallback(() => steps[selected], [steps, selected])
    const getNextWaypoint = useCallback(() => {
        let current = steps[selected]
        while (current && current.type != NodeType.WAYPOINT){
            if (!current.child)
                return undefined
            current = steps[current.child]
        }
        return current
    }, [steps, selected])
    const changeLabel = useCallback((id: string, label: string) => {
        setSteps(s => ({...s, [id]: {...s[id], label}}))
    }, [steps])
    const select = useCallback((id: string) => {
        const n = {...steps, [id]: {...steps[id], selected: true}}
        if(selected) n[selected].selected = false
        setSteps(n)
        setSelected(id)
    }, [selected, steps])
    const hasNext = useCallback(() => {
        if(!selected) return false;
        return !!steps[selected].child;

    }, [selected, steps])
    const next = useCallback(() => {
        if(!hasNext()) return;
        select(steps[selected].child as string)
    }, [selected, steps])

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
            "Initial State": {type: NodeType.START, predicates: [], label: "Initial State", selected: true},
        }),
        select,
        next,
        hasNext,
        getSelected,
        getNextWaypoint,
        append_new: (child) => add_new(selected, child)
    }}>
        {props.children}
    </NodeContext.Provider>

}