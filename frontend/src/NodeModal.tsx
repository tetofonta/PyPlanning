import React, {createContext, useCallback, useContext, useEffect, useState} from "react";
import {Predicate, useNodeContext} from "./NodeContext.tsx";
import {
    Button,
    Dialog,
    DialogActions,
    DialogContent,
    DialogContentText,
    DialogTitle, FormControl, IconButton, InputLabel, Select,
    TextField,
    Typography
} from "@mui/material";
import MenuItem from "@mui/material/MenuItem";
import {Add, Delete} from "@mui/icons-material";

export type NodeModalContextType = {
    show: (id: string) => void
}

const NodeModalContext = createContext<NodeModalContextType>({
    show: () => {
    }
})

export const useNodeModalContext = () => useContext(NodeModalContext)

const PredicateInput = (props: any) => {

    const {objects, id, add} = props

    const [formSelectedObj, setFormSelectedObj] = useState<string>("")
    const [formSelectedPred, setFormSelectedPred] = useState<string>("")
    const [formSelectedVal, setFormSelectedVal] = useState<string>("True")
    const [formSelectedParams, setFormSelectedParams] = useState<{[k: string]: string}>({})

    const [selectablePredicates, setSelectablePredicates] = useState<string[]>([])
    const [params, setParams] = useState<{[k: string]: string[]}>({})

    useEffect(() => {
        setFormSelectedObj("")
        setFormSelectedPred("")
        setFormSelectedVal("True")
        setSelectablePredicates([])
        setParams({})
    }, [id]);

    const onObjectSelected = useCallback((obj: string) => {
        setFormSelectedObj(obj)
        fetch(`/api/predicates/${objects[obj]}`)
            .then(res => res.json())
            .then(res => setSelectablePredicates(res))
    }, [formSelectedObj, objects])

    const onPredicateSelected = useCallback((pred: string) => {
        setFormSelectedPred(pred)
        fetch(`/api/params/${objects[formSelectedObj]}/${pred}`)
            .then(res => res.json())
            .then(res => setParams(res))
    }, [formSelectedObj, formSelectedPred])

    const onParamSelected = useCallback((param: string, value: string) => {
        setFormSelectedParams(params => ({...params, [param]: value}))
    }, [formSelectedParams])

    return <div style={{display: "flex"}}>
        <FormControl style={{width: '100%'}}>
            <InputLabel id="form-selected-object">Object</InputLabel>
            <Select
                labelId="form-selected-object"
                value={formSelectedObj}
                name="form_selected_object"
                label="Object"
                onChange={(e) => onObjectSelected(e.target.value)}
            >
                {Object.keys(objects || {}).map((k, i) => <MenuItem key={i} value={k}>{k}</MenuItem>)}
            </Select>
        </FormControl>
        <FormControl style={{width: '100%'}}>
            <InputLabel id="form-selected-predicate">Predicate</InputLabel>
            <Select
                labelId="form-selected-predicate"
                value={formSelectedPred}
                label="Predicate"
                onChange={(e) => onPredicateSelected(e.target.value)}
            >
                {selectablePredicates.map((k, i) => <MenuItem key={i} value={k}>{k}</MenuItem>)}
            </Select>
        </FormControl>
        {Object.keys(params).map((p, i) => <FormControl key={i} style={{width: '100%'}}>
            <InputLabel id={`form-selected-predicate-${p}`}>{p}</InputLabel>
            <Select
                labelId={`form-selected-predicate-${p}`}
                value={formSelectedParams[p]}
                label={p}
                onChange={(e) => onParamSelected(p, e.target.value)}
            >
                {params[p].map((k, i) => <MenuItem key={`${p}-${i}`} value={k}>{k}</MenuItem>)}
            </Select>
        </FormControl>)}

        <FormControl style={{width: '100%'}}>
            <InputLabel id="form-selected-value">Value</InputLabel>
            <Select
                labelId="form-selected-value"
                value={formSelectedVal}
                label="Value"
                onChange={(e) => setFormSelectedVal(e.target.value)}
            >
                <MenuItem value="True">True</MenuItem>
                <MenuItem value="False">False</MenuItem>
            </Select>
        </FormControl>

        <IconButton onClick={() => {
            add({
                object: formSelectedObj,
                predicate: formSelectedPred,
                params: formSelectedParams,
                value: formSelectedVal == "True"
            })
            setFormSelectedObj("")
            setFormSelectedPred("")
            setFormSelectedVal("True")
        }}><Add/></IconButton>
    </div>
}

export const NodeModalContextProvider = (props: { children: React.ReactElement | React.ReactElement[] }) => {

    const [id, setId] = useState<string | null>(null)
    const [statePredicates, setStatePredicates] = useState<Predicate[]>([])
    const [objects, setObjects] = useState<{ [k: string]: string }>({})
    const nodeContext = useNodeContext()

    const show = useCallback((id: string) => {
        setId(id)

        console.log(nodeContext.get(id)?.predicates)
        setStatePredicates(nodeContext.get(id)?.predicates || [])
    }, [nodeContext])
    useEffect(() => {
        fetch("/api/objects").then((res) => res.json()).then(async (data: any) => {
            setObjects(data)
        })
    }, []);

    return <NodeModalContext.Provider value={{
        show
    }}>
        {props.children}
        <Dialog
            open={!!id}
            onClose={() => setId(null)}
            PaperProps={{
                component: 'form',
                style: {minWidth: '75vw'},
                onSubmit: (event: React.FormEvent<HTMLFormElement>) => {
                    event.preventDefault();

                    const formData = new FormData(event.currentTarget);
                    const formJson = Object.fromEntries((formData as any).entries());

                    if (formJson.node_id != id)
                        nodeContext.changeLabel(id || "", formJson.node_id)

                    nodeContext.setPredicates(id || "", JSON.parse(formJson.predicates))

                    setId(null);
                },
            }}
        >
            <DialogTitle>Edit Node</DialogTitle>
            <DialogContent>
                <DialogContentText><Typography variant="overline">Edit node id: {id}</Typography></DialogContentText>
                <TextField autoFocus required margin="dense" name="node_id" label="Node ID" type="text" fullWidth
                           variant="standard" defaultValue={nodeContext.get(id || "")?.label}/>
                <Typography>Predicates</Typography>

                {statePredicates.map((o, i) => <div style={{display: "flex", alignItems: "center"}}><Typography
                    key={i}>{o.object}.{o.predicate}({Object.keys(o.params).map(e => `${e}=${o.params[e]}`)}) = {o.value ? "True" : "False"}</Typography>
                    <IconButton
                        onClick={() => {
                            console.log("AAAAAAAAAAAAAAAAAAAAA", i)
                            setStatePredicates(p => {
                                const a = [...p]
                                a.splice(i, 1)
                                return a
                            })
                        }}><Delete/></IconButton></div>)}

                <input type="hidden" value={JSON.stringify(statePredicates)} name="predicates"/>

                <PredicateInput objects={objects} id={id} add={(e: Predicate) => setStatePredicates(p => [...p, e])} />
            </DialogContent>
            <DialogActions>
                <Button onClick={() => setId(null)}>Cancel</Button>
                <Button type="submit">Commit</Button>
            </DialogActions>
        </Dialog>
    </NodeModalContext.Provider>
}