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

export type PDDLGraphAction = PDDLGraphData & {
    name: string,
    params: string[]
    user: boolean
    user_message: string
}

export type PDDLGraphCondition = PDDLGraphData & {
    text: string,
    childFalse?: string
    result?: boolean
    hasResult?: boolean
}


export type PDDLGraphNode = GraphNode & PDDLGraphData

export type NodeContextType = {
    nodes: PDDLGraphNode[];
    edges: GraphEdge[];
    selected: string,
    add_new: (father: string|null, child: Omit<PDDLGraphNode, "id">) => string;
    connect: (father: string, child: string, field?: string) => void;
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
    plan: (id?: string) => void;
    execute: (single_step: boolean, id?: string) => void;
    reset: () => void;
}

export const NodeContext = createContext<NodeContextType>({
    nodes: [],
    edges: [],
    add_new: () => "",
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
    plan: () => {
    },
    execute: () => {
    },
    getSelected: () => undefined,
    getNextWaypoint: () => undefined,
    hasNext: () => false,
    selected: "",
    connect: () => {
    }
})

export const useNodeContext = () => useContext(NodeContext)

export enum NodeType {
    START,
    WAYPOINT,
    ACTION,
    CONDITION
}

const getNodeFromStep = (id: string, step: PDDLGraphData): PDDLGraphNode => {
    switch (step.type) {
        case NodeType.START:
            return {
                id,
                fill: "#F00",
                ...step,
                label: step.selected ? `[${step.label || id}]` : (step.label || id)
            }
        case NodeType.WAYPOINT:
            return {
                id,
                fill: "#123",
                ...step,
                label: step.selected ? `[${step.label || id}]` : (step.label || id)
            }
        case NodeType.ACTION:
            return {
                id,
                fill: "#3e7cb6",
                ...step,
                label: step.selected ? `[${step.label || id}]` : (step.label || id),
                size: 6
            }
        case NodeType.CONDITION:
            return {
                id,
                fill: "#b68e3e",
                ...step,
                label: step.selected ? `[${step.label || id}]` : (step.label || id),
            }
    }
}

const getEdges = (start: string, steps: {
    [k: string]: PDDLGraphData
}): GraphEdge[] => {
    const ret: GraphEdge[] = []
    const inserted_nodes = new Set([start])
    const stack = [start]

    while (stack.length > 0) {
        const a_k = stack.pop() as string

        //todo handle multi child graph
        // @ts-ignore
        const b_ks = [{child: steps[a_k].child}, {child: steps[a_k].childFalse, label: "False"}].filter(e => !!(e && e.child))
        b_ks.forEach((b_k: any) => {
            ret.push({
                id: `${a_k}->${b_k.child}`,
                source: a_k,
                target: b_k.child,
                label: b_k.label
            })
            if (inserted_nodes.has(b_k.child)) return
            stack.push(b_k.child)
            inserted_nodes.add(b_k.child)
        })
    }
    return ret
}

function add_new_internal(steps: any, father: string|null, child: PDDLGraphData) {

    const id = Math.random().toString(26).substring(2)
    return [Object.assign({
        ...steps,
        [id]: {...child, father, child: father ? steps[father].child : undefined}
    }, father ? {[father]: {...steps[father], child: id}} : {}), id]
}

async function execute_internal(action: PDDLGraphAction) {
    if (action.user)
        return alert(action.user_message)

    await fetch(`/api/execute/${action.name}`, {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify(action.params)
    })
}

export const NodeContextProvider = (props: { children: React.ReactElement | React.ReactElement[] }) => {

    const [steps, setSteps] = useState<{ [k: string]: PDDLGraphData }>({
        "Initial State": {type: NodeType.START, predicates: [], label: "Initial State", selected: true},
    })
    const [selected, setSelected] = useState<string>("Initial State")

    const add_new = useCallback((father: string|null, child: Omit<PDDLGraphNode, "id">) => {
        const [s, id] = add_new_internal(steps, father, child)
        setSteps(s);
        return id
    }, [steps])
    const connect = useCallback((father: string, child: string, field: string = "child") => {
        console.log({...steps, [father]: {...steps[father], [field]: child}, [child]: {...steps[child], father}})
        setSteps(s => ({...s, [father]: {...s[father], [field]: child}, [child]: {...s[child], father}}))
    }, [steps, selected])
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
        while (current && current.type != NodeType.WAYPOINT) {
            if (!current.child)
                return undefined
            current = steps[current.child]
        }
        return current
    }, [steps, selected])
    const changeLabel = useCallback((id: string, label: string) => {
        setSteps(s => ({...s, [id]: {...s[id], label}}))
    }, [steps, selected])
    const select = useCallback((id: string) => {
        const n = {...steps, [id]: {...steps[id], selected: true}}
        console.log(steps, n)
        if (selected) n[selected].selected = false
        setSteps(n)
        setSelected(id)
    }, [selected, steps])
    const hasNext = useCallback(() => {
        if (!selected) return false;
        return !!steps[selected].child;

    }, [selected, steps])
    const next = useCallback(() => {
        console.log(steps, selected)
        if (!hasNext()) return;
        select(steps[selected].child as string)
    }, [selected, steps])

    const plan = useCallback((id?: string) => {
        id = id ?? selected
        let child = steps[id].child
        const next_steps = {...steps}

        if(next_steps[id].type == NodeType.CONDITION){
            const res = (next_steps[id] as PDDLGraphCondition).hasResult ? (next_steps[id] as PDDLGraphCondition).result : confirm((next_steps[id] as PDDLGraphCondition).text);
            (next_steps[id] as PDDLGraphCondition).hasResult = true;
            (next_steps[id] as PDDLGraphCondition).result = res;

            if(res && next_steps[id].child) {
                child = next_steps[id].child
            } else if (!res && (next_steps[id] as PDDLGraphCondition).childFalse) {
                child = (next_steps[id] as PDDLGraphCondition).childFalse
            } else
                return;
        }

        const next_node = child
        if (!next_node || !next_steps[next_node]) return;

        // remove all actions in this transition
        let cur_node = next_node
        while (next_steps[cur_node].type == NodeType.ACTION) {
            const ch = next_steps[cur_node].child
            delete next_steps[cur_node]
            if (!ch) return

            cur_node = ch
            next_steps[id].child = ch
            next_steps[ch].father = id
        }

        fetch("/api/plan", {
            method: 'POST',
            headers: {'Content-Type': "application/json"},
            body: JSON.stringify(getNextWaypoint()?.predicates)
        })
            .then(res => res.json())
            .then(data => {
                return data.reverse().reduce((a: string, e: any) => {
                    console.log(a)
                    return add_new_internal(a[0], id, {
                        type: NodeType.ACTION,
                        predicates: [],
                        selected: false,
                        label: `${e.user ? "USER: " : ""}${e.params[0]}.${e.action}(${e.params.slice(1).join(", ")})`,
                        user: e.user,
                        user_message: e.user_message || "",
                        name: e.action,
                        params: e.params
                    } as PDDLGraphAction)
                }, [next_steps, ""])
            })
            .then(([steps, id]) => {
                if (id) {
                    steps[selected].selected = false
                    steps[id].selected = true
                    setSelected(id)
                }
                setSteps(steps)
            }).catch(() => {
        })
    }, [steps, selected])
    const execute = useCallback(async (single_step: boolean, id?: string) => {
        id = id ?? selected

        const s = {...steps}
        s[selected].selected = false
        s[id].selected = true
        setSelected(id)
        setSteps(s)

        
        if(s[id].type == NodeType.CONDITION){
            const res = (s[id] as PDDLGraphCondition).hasResult ? ((s[id] as PDDLGraphCondition).result) : confirm((s[id] as PDDLGraphCondition).text);
            (s[id] as PDDLGraphCondition).hasResult = true;
            (s[id] as PDDLGraphCondition).result = res;

            if(res && s[id].child) {
                s[id].selected = false
                s[s[id].child as string].selected = true
                setSelected(s[id].child as string)
            } else if (!res && (s[id] as PDDLGraphCondition).childFalse) {
                s[id].selected = false
                s[(s[id] as PDDLGraphCondition).childFalse as string].selected = true
                setSelected((s[id] as PDDLGraphCondition).childFalse as string)
            }
            setSteps(s)
            return
        }

        let cur_node: string | undefined = id
        while (cur_node && s[cur_node].type != NodeType.ACTION) {
            if (!s[cur_node].child) return

            s[cur_node].selected = false
            cur_node = s[cur_node].child as string
            s[cur_node].selected = true
            setSelected(cur_node)
            setSteps(s)

            if (single_step) return
        }

        if (!cur_node)
            return

        while (cur_node && s[cur_node].type == NodeType.ACTION) {
            try {
                await execute_internal(s[cur_node] as PDDLGraphAction)
            } catch (e) {
                alert(`Action ${s[cur_node].label} failed`)
                return
            }

            if (!s[cur_node].child) return

            s[cur_node].selected = false
            cur_node = steps[cur_node].child as string
            s[cur_node].selected = true

            setSelected(cur_node)
            setSteps(s)

            if (single_step) return
        }
    }, [steps, selected])

    const nodes = useMemo(() => Object.keys(steps).map(k => getNodeFromStep(k, steps[k])), [steps, selected])
    const edges = useMemo(() => getEdges("Initial State", steps), [steps, selected])

    return <NodeContext.Provider value={{
        nodes,
        edges,
        add_new,
        remove,
        setPredicates,
        get,
        changeLabel: changeLabel,
        reset: () => {
            setSelected("Initial State")
            setSteps({
                "Initial State": {type: NodeType.START, predicates: [], label: "Initial State", selected: true},
            })
        },
        select,
        next,
        hasNext,
        getSelected,
        getNextWaypoint,
        plan,
        execute,
        append_new: (child) => add_new(selected, child),
        selected,
        connect
    }}>
        {props.children}
    </NodeContext.Provider>

}