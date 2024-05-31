import Divider from '@mui/material/Divider';
import Paper from '@mui/material/Paper';
import MenuList from '@mui/material/MenuList';
import MenuItem from '@mui/material/MenuItem';
import ListItemText from '@mui/material/ListItemText';
import ListItemIcon from '@mui/material/ListItemIcon';
import {Add, ArrowDownward, ArrowUpward, CheckBox, Close, Delete, Edit} from "@mui/icons-material"
import {NodeContextType, NodeType, PDDLGraphCondition, PDDLGraphNode} from "./NodeContext.tsx";
import {NodeModalContextType} from "./NodeModal.tsx";
import {useEffect, useState} from "react";

export type NodeMenuProps = {
    node: PDDLGraphNode;
    onClose: () => void,
    nodeContext: NodeContextType,
    nodeModalContext: NodeModalContextType,
    graphContainerRef: any
};

export const NodeMenu = (props: NodeMenuProps) => {

    const {nodeContext, onClose, node, nodeModalContext, graphContainerRef} = props;
    const [connectOpen, setConnectOpen] = useState(false)
    const [connectConditionOpen, setConnectConditionOpen] = useState(false)

    useEffect(() => {
        if (!graphContainerRef.current)
            return
        const canvas = graphContainerRef.current.getElementsByTagName("canvas")[0];
        canvas.onclick = () => onClose()
    }, [graphContainerRef])

    return <Paper sx={{width: 320, maxWidth: '100%', position: 'relative', left: 160, top: 168 / 2}}>
        <MenuList>
            <MenuItem onClick={props.onClose}>
                <ListItemIcon>
                    <Close fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Close Menu</ListItemText>
            </MenuItem>
            <Divider/>

            <MenuItem onClick={() => {
                nodeContext.add_new(node.id, {
                    type: NodeType.WAYPOINT,
                    label: "New State",
                    predicates: []
                })
                onClose()
            }}>
                <ListItemIcon>
                    <Add fontSize="small"/>
                </ListItemIcon>
                <ListItemText>New Waypoint</ListItemText>
            </MenuItem>

            <MenuItem onClick={() => {
                const text = prompt("Insert message prompt")
                nodeContext.add_new(node.id, {
                    type: NodeType.CONDITION,
                    label: "New Condition",
                    predicates: [],
                    text: text || "",
                } as PDDLGraphCondition)
                onClose()
            }}>
                <ListItemIcon>
                    <Add fontSize="small"/>
                </ListItemIcon>
                <ListItemText>New Condition</ListItemText>
            </MenuItem>

            <MenuItem onClick={() => {
                setConnectOpen(!connectOpen)
            }}>
                <ListItemIcon>
                    {!connectOpen && <ArrowDownward fontSize="small"/>}
                    {connectOpen && <ArrowUpward fontSize="small"/>}
                </ListItemIcon>
                <ListItemText>Connect...</ListItemText>
            </MenuItem>

            <div style={{transition: ".3s ease", height: connectOpen ? 200 : 0, overflow: 'scroll'}}>
                {connectOpen && <MenuList>
                    {nodeContext.nodes.filter(e => e.id != "Initial State" && e.id != node.id).map(e => <MenuItem onClick={() => {
                        nodeContext.connect(node.id, e.id)
                        // console.log(node.id, e.id)
                    }}><ListItemText>{e.label}</ListItemText></MenuItem>)}
                </MenuList>}
            </div>

            {node.type === NodeType.CONDITION && [
                <MenuItem onClick={() => {
                    setConnectConditionOpen(!connectConditionOpen)
                }}>
                    <ListItemIcon>
                        {!connectConditionOpen && <ArrowDownward fontSize="small"/>}
                        {connectConditionOpen && <ArrowUpward fontSize="small"/>}
                    </ListItemIcon>
                    <ListItemText>Connect False Branch...</ListItemText>
                </MenuItem>,

                <div style={{transition: ".3s ease", height: connectConditionOpen ? 200 : 0, overflow: 'scroll'}}>
                    {connectConditionOpen && <MenuList>
                        {nodeContext.nodes.filter(e => e.id != "Initial State" && e.id != node.id).map(e => <MenuItem onClick={() => {
                            nodeContext.connect(node.id, e.id, "childFalse")
                            // console.log(node.id, e.id)
                        }}><ListItemText>{e.label}</ListItemText></MenuItem>)}
                    </MenuList>}
                </div>
            ]}

            {node.type !== NodeType.START && <MenuItem onClick={() => {
                nodeContext.remove(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <Delete fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Delete Node</ListItemText>
            </MenuItem>
            }

            {node.type !== NodeType.START && <MenuItem onClick={() => {
                nodeModalContext.show(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <Edit fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Edit Node</ListItemText>
            </MenuItem>
            }

            {!node.selected && <MenuItem onClick={() => {
                nodeContext.select(node.id)
                onClose()
            }}>
                <ListItemIcon>
                    <CheckBox fontSize="small"/>
                </ListItemIcon>
                <ListItemText>Select</ListItemText>
            </MenuItem>}

        </MenuList>
    </Paper>
}