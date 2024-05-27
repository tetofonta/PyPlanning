import {GraphCanvas, recommendLayout} from "reagraph"
import {AppBar, IconButton, Toolbar, Typography} from "@mui/material";
import "./style/app.sass"
import {NodeMenu} from "./NodeMenu.tsx";
import {NodeContextProvider, PDDLGraphNode, useNodeContext} from "./NodeContext.tsx";
import {Refresh} from "@mui/icons-material"
import {NodeModalContextProvider, useNodeModalContext} from "./NodeModal.tsx";
import {useRef} from "react";

const Content = () => {

    const nodeContext = useNodeContext()
    const nodeModalContext = useNodeModalContext()
    const graphRef = useRef() as any
    const layout = recommendLayout(nodeContext.nodes, nodeContext.edges);

    return <>
        <AppBar position="fixed" sx={{ zIndex: (theme) => theme.zIndex.drawer + 1 }} className="navbar">
            <Toolbar>
                <Typography
                    variant="h6"
                    noWrap
                    component="a"
                    sx={{
                        mr: 2,
                        display: {xs: 'none', md: 'flex'},
                        fontFamily: 'monospace',
                        fontWeight: 700,
                        letterSpacing: '.3rem',
                        textDecoration: 'none',
                    }}
                >
                    AI-ROB
                </Typography>
                <div className="toolbar">
                    <IconButton style={{color: "#FFF"}} onClick={() => {
                        if (confirm("Everything will be lost, even your mental sanity. Are you sure to continue?"))
                            nodeContext.reset()
                    }}>
                        <Refresh/>
                    </IconButton>
                </div>
            </Toolbar>
        </AppBar>
        <div ref={graphRef} className="graph" style={{position: 'relative'}}>
            <GraphCanvas
                nodes={nodeContext.nodes}
                edges={nodeContext.edges}
                layoutType={layout}
                contextMenu={({data, onClose}) =>
                    <NodeMenu nodeContext={nodeContext} nodeModalContext={nodeModalContext}
                              node={data as unknown as PDDLGraphNode} onClose={onClose} graphContainerRef={graphRef}/>}
                onNodeDoubleClick={(node) => {
                    if (node.id != "Initial State")
                        nodeModalContext.show(node.id)
                }}
                draggable
            />
        </div>
    </>
}

function App() {


    return (
        <NodeContextProvider>
            <NodeModalContextProvider>
                <Content/>
            </NodeModalContextProvider>
        </NodeContextProvider>
    )
}

export default App
